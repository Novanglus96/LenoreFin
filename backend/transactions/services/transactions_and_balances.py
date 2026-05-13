from datetime import date
from typing import List, Optional, Tuple
from transactions.api.schemas.transaction import TransactionOut
from accounts.models import Account
from transactions.models import (
    Transaction,
    ReminderCacheTransaction,
    ForecastCacheTransaction,
)
from utils.dates import (
    get_todays_date_timezone_adjusted,
)
from transactions.api.dependencies.transaction_utilities import (
    sort_transaction_list,
    add_balances_to_transaction_list,
    annotate_transaction_display_info,
    annotate_transaction_total,
    annotate_transaction_total_for_parent,
    add_tags_to_transactions,
    sort_transactions,
    annotate_transaction_balance,
)
from decimal import Decimal
from django.db.models import Q, Case, When, Sum, F, DecimalField
from django.core.cache import cache
from django.db.models.functions import Abs
from core.cache.keys import (
    account_combined_transactions,
    account_forecast_transactions,
    account_reminder_transactions,
    account_cleared_balance,
    account_pending_balance,
    account_real_transactions,
)
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")


def get_account_transactions_and_balances(
    end_date: date,
    account_id: int,
    totals_only: bool,
    forecast: Optional[bool] = False,
    start_date: Optional[date] = None,
    cleared_only: Optional[bool] = False,
) -> Tuple[List[TransactionOut], Decimal]:
    """
    The function `get_transactions_by_account` returns a list of
    transactions, temporary reminder transactions, etc.

    Args:
        start_date (Date): The first date of the transactions.
        end_date (Date): The last date of the transactions.
        account (Int): The ID of the account to get transactions for.

    Returns:
        transactions: List of transaction objects
    """
    # Delegate to the parent-account handler when this account has children
    if Account.objects.filter(parent_account_id=account_id).exists():
        return get_parent_account_transactions_and_balances(
            end_date, account_id, totals_only, forecast, start_date
        )

    # Forecast results depend on async task completion — skip cache to ensure freshness.
    use_cache = not forecast
    key = f"{account_combined_transactions(account_id)}:{end_date}:{totals_only}:{forecast}:{start_date}:{cleared_only}"
    if use_cache:
        data = cache.get(key)
        if data:
            return data

    # Setup variables
    today = get_todays_date_timezone_adjusted()
    reminder_transactions_list = []
    cleared_transactions_list = []
    pending_transactions_list = []

    # Check if account exists.  Return an empty list if not.
    try:
        account = Account.objects.get(id=account_id)
    except Account.DoesNotExist:
        return [], Decimal(0.00)

    # Get Account Info
    opening_balance = account.opening_balance
    archive_balance = account.archive_balance

    # Get All transacitons
    all_transactions = Transaction.objects.filter(
        Q(source_account_id=account_id) | Q(destination_account_id=account_id),
        transaction_date__lt=end_date,
    ).exclude(status__slug='archived').select_related("status", "transaction_type")

    # Get Reminder transactions
    reminder_transactions = ReminderCacheTransaction.objects.filter(
        Q(source_account_id=account_id) | Q(destination_account_id=account_id),
        transaction_date__lt=end_date,
    ).exclude(status__slug='archived').select_related("status", "transaction_type")

    # Get Forecast transactions
    forecast_transactions = ForecastCacheTransaction.objects.filter(
        Q(source_account_id=account_id) | Q(destination_account_id=account_id),
        transaction_date__lt=end_date,
    ).exclude(status__slug='archived').select_related("status", "transaction_type")

    # If not totals only, annotate transactions with pretty information
    if not totals_only:
        all_transactions = annotate_transaction_display_info(all_transactions)
        reminder_transactions = annotate_transaction_display_info(
            reminder_transactions
        )
        forecast_transactions = annotate_transaction_display_info(
            forecast_transactions
        )

    # Annotate pretty totals
    all_transactions = annotate_transaction_total(all_transactions, account_id)
    reminder_transactions = annotate_transaction_total(
        reminder_transactions, account_id
    )
    forecast_transactions = annotate_transaction_total(
        forecast_transactions, account_id
    )

    # Add tags to cleared transactions if not totals_only
    if not totals_only:
        reminder_transactions = add_tags_to_transactions(
            reminder_transactions, "r"
        )
        forecast_transactions = add_tags_to_transactions(
            forecast_transactions, "f"
        )

    # Sort and get balances for cleared transactions
    cleared_transactions = all_transactions.exclude(status__slug='pending')
    cleared_transactions = sort_transactions(cleared_transactions, True)
    cleared_transactions = annotate_transaction_balance(
        cleared_transactions, opening_balance, archive_balance
    )
    cleared_balance = opening_balance + archive_balance
    if cleared_transactions:
        cleared_balance = (
            cleared_transactions.order_by(
                "custom_order", "transaction_date", "-pretty_total", "-id"
            )
            .last()
            .balance
        )
    if not totals_only:
        cleared_transactions = add_tags_to_transactions(
            cleared_transactions, "t"
        )

    # Get pending transactions
    pending_transactions = all_transactions.filter(status__slug='pending')
    if not totals_only:
        pending_transactions = add_tags_to_transactions(
            pending_transactions, "t"
        )

    # Create lists of TransactionOut objects
    cleared_transactions_list = [
        TransactionOut.from_orm(obj) for obj in cleared_transactions
    ]
    pending_transactions_list = [
        TransactionOut.from_orm(obj) for obj in pending_transactions
    ]
    reminder_transactions_list = [
        TransactionOut.from_orm(obj).model_copy(
            update={"id": -obj.id, "simulated": True}
        )
        for obj in reminder_transactions
    ]
    forecast_transactions_list = [
        TransactionOut.from_orm(obj) for obj in forecast_transactions
    ]
    forecast_transactions_list = [
        TransactionOut.from_orm(obj).model_copy(
            update={"id": -obj.id - 10000, "simulated": True}
        )
        for obj in forecast_transactions
    ]

    # Combine lists to be sorted
    transactions_to_be_sorted = (
        pending_transactions_list
        + reminder_transactions_list
        + forecast_transactions_list
    )

    # Sort transactions
    sorted_transactions = sort_transaction_list(transactions_to_be_sorted)

    # Add balances to sorted transactions
    sorted_transactions_with_balances = add_balances_to_transaction_list(
        sorted_transactions, cleared_balance
    )

    # Add cleared and pending
    transactions = cleared_transactions_list + sorted_transactions_with_balances

    # Filter transactions for status and greater than start date, record previous balance
    if forecast:

        def filter_new_transactions(transactions, start_date):
            # Filter the transactions where transaction_date is greater than today
            return [
                transaction
                for transaction in transactions
                if transaction.transaction_date
                and transaction.transaction_date >= start_date
            ]

        def filter_previous_transactions(transactions, start_date):
            # Filter the transactions where transaction_date is greater than today
            return [
                transaction
                for transaction in transactions
                if transaction.transaction_date
                and transaction.transaction_date < start_date
            ]

        previous_balance = opening_balance + archive_balance
        if start_date:
            start = start_date
        else:
            start = today
        filtered_transactions = filter_new_transactions(transactions, start)
        previous_transactions = filter_previous_transactions(
            transactions, start
        )
        if previous_transactions:
            if isinstance(
                previous_transactions[-1],
                dict,
            ):
                previous_balance = previous_transactions[-1]["balance"]
            else:
                previous_balance = previous_transactions[-1].balance
        my_tuple = (filtered_transactions, previous_balance)
        return my_tuple
    else:
        my_tuple = (transactions, Decimal(0.00))
        if use_cache:
            cache.set(key, my_tuple, timeout=60 * 60)
        return my_tuple


def get_parent_account_transactions_and_balances(
    end_date: date,
    account_id: int,
    totals_only: bool,
    forecast: bool = False,
    start_date: Optional[date] = None,
) -> Tuple[List[TransactionOut], Decimal]:
    """
    Returns combined transactions for a parent account by merging all children.
    Internal transfers between children are excluded — they net to zero in the
    combined view and don't exist at the bank statement level.
    """
    use_cache = not forecast
    key = f"{account_combined_transactions(account_id)}:parent:{end_date}:{totals_only}:{forecast}:{start_date}"
    if use_cache:
        data = cache.get(key)
        if data:
            return data

    today = get_todays_date_timezone_adjusted()

    children = Account.objects.filter(parent_account_id=account_id)
    child_ids = list(children.values_list('id', flat=True))

    if not child_ids:
        return [], Decimal(0.00)

    opening_balance = sum(c.opening_balance or Decimal(0) for c in children)
    archive_balance = sum(c.archive_balance or Decimal(0) for c in children)

    # Transfers where both sides are children cancel out in the combined view
    internal_transfer_q = Q(
        transaction_type__slug='transfer',
        source_account_id__in=child_ids,
        destination_account_id__in=child_ids,
    )

    touch_any_child = Q(source_account_id__in=child_ids) | Q(destination_account_id__in=child_ids)

    all_transactions = (
        Transaction.objects.filter(touch_any_child, transaction_date__lt=end_date)
        .exclude(status__slug='archived')
        .exclude(internal_transfer_q)
        .select_related("status", "transaction_type")
    )
    reminder_transactions = (
        ReminderCacheTransaction.objects.filter(touch_any_child, transaction_date__lt=end_date)
        .exclude(status__slug='archived')
        .exclude(internal_transfer_q)
        .select_related("status", "transaction_type")
    )
    forecast_transactions = (
        ForecastCacheTransaction.objects.filter(touch_any_child, transaction_date__lt=end_date)
        .exclude(status__slug='archived')
        .exclude(internal_transfer_q)
        .select_related("status", "transaction_type")
    )

    if not totals_only:
        all_transactions = annotate_transaction_display_info(all_transactions)
        reminder_transactions = annotate_transaction_display_info(reminder_transactions)
        forecast_transactions = annotate_transaction_display_info(forecast_transactions)

    all_transactions = annotate_transaction_total_for_parent(all_transactions, child_ids)
    reminder_transactions = annotate_transaction_total_for_parent(reminder_transactions, child_ids)
    forecast_transactions = annotate_transaction_total_for_parent(forecast_transactions, child_ids)

    if not totals_only:
        reminder_transactions = add_tags_to_transactions(reminder_transactions, "r")
        forecast_transactions = add_tags_to_transactions(forecast_transactions, "f")

    cleared_transactions = all_transactions.exclude(status__slug='pending')
    cleared_transactions = sort_transactions(cleared_transactions, True)
    cleared_transactions = annotate_transaction_balance(cleared_transactions, opening_balance, archive_balance)
    cleared_balance = opening_balance + archive_balance
    if cleared_transactions:
        cleared_balance = (
            cleared_transactions.order_by("custom_order", "transaction_date", "-pretty_total", "-id")
            .last()
            .balance
        )
    if not totals_only:
        cleared_transactions = add_tags_to_transactions(cleared_transactions, "t")

    pending_transactions = all_transactions.filter(status__slug='pending')
    if not totals_only:
        pending_transactions = add_tags_to_transactions(pending_transactions, "t")

    cleared_transactions_list = [TransactionOut.from_orm(obj) for obj in cleared_transactions]
    pending_transactions_list = [TransactionOut.from_orm(obj) for obj in pending_transactions]
    reminder_transactions_list = [
        TransactionOut.from_orm(obj).model_copy(update={"id": -obj.id, "simulated": True})
        for obj in reminder_transactions
    ]
    forecast_transactions_list = [
        TransactionOut.from_orm(obj).model_copy(update={"id": -obj.id - 10000, "simulated": True})
        for obj in forecast_transactions
    ]

    transactions_to_be_sorted = pending_transactions_list + reminder_transactions_list + forecast_transactions_list
    sorted_transactions = sort_transaction_list(transactions_to_be_sorted)
    sorted_transactions_with_balances = add_balances_to_transaction_list(sorted_transactions, cleared_balance)
    transactions = cleared_transactions_list + sorted_transactions_with_balances

    if forecast:
        def filter_new(txns, start):
            return [t for t in txns if t.transaction_date and t.transaction_date >= start]

        def filter_prev(txns, start):
            return [t for t in txns if t.transaction_date and t.transaction_date < start]

        previous_balance = opening_balance + archive_balance
        start = start_date or today
        filtered = filter_new(transactions, start)
        previous = filter_prev(transactions, start)
        if previous:
            previous_balance = previous[-1].balance if not isinstance(previous[-1], dict) else previous[-1]["balance"]
        return (filtered, previous_balance)
    else:
        result = (transactions, Decimal(0.00))
        if use_cache:
            cache.set(key, result, timeout=60 * 60)
        return result


def fetch_account_transactions(account_id: int, transactions_type: str):
    """
    The function `get_transactions_by_account` returns a list of
    transactions, temporary reminder transactions, etc.

    Args:
        start_date (Date): The first date of the transactions.
        end_date (Date): The last date of the transactions.
        account (Int): The ID of the account to get transactions for.

    Returns:
        transactions: List of transaction objects
    """
    transactions = None

    # Check Cache
    key = None

    if transactions_type == "transaction":
        key = account_real_transactions(account_id)
    if transactions_type == "reminder":
        key = account_reminder_transactions(account_id)
    if transactions_type == "forecast":
        key = account_forecast_transactions(account_id)

    data = cache.get(key)
    if data:
        return data

    if transactions_type == "transaction":
        # Get transaction transacitons
        transactions = Transaction.objects.filter(
            Q(source_account_id=account_id)
            | Q(destination_account_id=account_id)
        ).exclude(status__transaction_status="Archived")

    if transactions_type == "reminder":
        # Get transaction transacitons
        transactions = ReminderCacheTransaction.objects.filter(
            Q(source_account_id=account_id)
            | Q(destination_account_id=account_id)
        ).exclude(status__transaction_status="Archived")

    if transactions_type == "forecast":
        # Get transaction transacitons
        transactions = ForecastCacheTransaction.objects.filter(
            Q(source_account_id=account_id)
            | Q(destination_account_id=account_id)
        ).exclude(status__transaction_status="Archived")

    cache.set(key, transactions, timeout=60 * 60)
    return transactions


def get_account_cleared_balance(account_id: int):
    # Check Cache
    key = account_cleared_balance(account_id)
    data = cache.get(key)
    if data:
        return data

    qs = Account.objects.filter(id=account_id)
    if not qs.exists():
        raise AccountNotFound()

    account = qs.first()
    transactions = fetch_account_transactions(account_id, "transaction")
    cleared_transactions = transactions.exclude(
        status__transaction_status="Pending"
    )
    result = cleared_transactions.aggregate(
        balance=Sum(
            Case(
                When(
                    source_account_id=account_id,
                    then=F("total_amount"),
                ),
                When(
                    destination_account_id=account_id,
                    then=Abs(F("total_amount")),
                ),
                output_field=DecimalField(),
            )
        )
    )
    cleared_balance = (
        (result["balance"] or Decimal("0"))
        + account.archive_balance
        + account.opening_balance
    )
    cache.set(key, cleared_balance, timeout=60 * 60)
    return cleared_balance


def get_account_pending_balance(account_id: int):
    # Check Cache
    key = account_pending_balance(account_id)
    data = cache.get(key)
    if data:
        return data

    qs = Account.objects.filter(id=account_id)
    if not qs.exists():
        raise AccountNotFound()

    account = qs.first()
    today = get_todays_date_timezone_adjusted()
    transactions = fetch_account_transactions(account_id, "transaction")
    filtered_transactions = transactions.filter(transaction_date__lte=today)
    result = filtered_transactions.aggregate(
        balance=Sum(
            Case(
                When(
                    source_account_id=account_id,
                    then=F("total_amount"),
                ),
                When(
                    destination_account_id=account_id,
                    then=Abs(F("total_amount")),
                ),
                output_field=DecimalField(),
            )
        )
    )
    pending_balance = (
        (result["balance"] or Decimal("0"))
        + account.archive_balance
        + account.opening_balance
    )
    cache.set(key, pending_balance, timeout=60 * 60)
    return pending_balance


class AccountNotFound(Exception):
    pass
