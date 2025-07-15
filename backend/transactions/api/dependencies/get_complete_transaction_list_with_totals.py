from decimal import Decimal
from typing import List, Optional, Dict, Any
from datetime import date, timedelta, datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from administration.api.dependencies.get_todays_date_timezone_adjusted import (
    get_todays_date_timezone_adjusted,
)
from accounts.models import Account
from django.db.models import (
    Case,
    When,
    Q,
    IntegerField,
    Value,
    F,
    CharField,
    Sum,
    Subquery,
    OuterRef,
    FloatField,
    Window,
    ExpressionWrapper,
    DecimalField,
    Func,
    Count,
)
from transactions.models import Transaction, TransactionDetail
from django.db.models.functions import Concat, Coalesce, Abs
from transactions.api.dependencies.get_reminder_transaction_list import (
    get_reminder_transaction_list,
)
from transactions.api.dependencies.add_balances_to_transaction_list import (
    add_balances_to_transaction_list,
)
from transactions.api.dependencies.sort_transaction_list import (
    sort_transaction_list,
)
from transactions.api.dependencies.forecast_transaction import (
    ForecastTransaction,
)


def get_complete_transaction_list_with_totals(
    end_date: date,
    account: int,
    totals_only: bool,
    forecast: Optional[bool] = False,
    start_date: Optional[date] = None,
    transfers_only: Optional[bool] = False,
    transfer_ids: Optional[List[int]] = [],
    tags: Optional[List[int]] = [],
    cleared_only: Optional[bool] = False,
):
    """
    The function `get_complete_transaction_list_with_totals` returns a list of
    transactions, temporary reminder transactions, etc.

    Args:
        start_date (Date): The first date of the transactions.
        end_date (Date): The last date of the transactions.
        account (Int): The ID of the account to get transactions for.

    Returns:
        transactions: List of transaction objects
    """

    # Setup variables
    today = get_todays_date_timezone_adjusted()

    # Subqueries
    source_account_name = Account.objects.filter(
        id=OuterRef("source_account_id")
    ).values("account_name")[:1]
    destination_account_name = Account.objects.filter(
        id=OuterRef("destination_account_id")
    ).values("account_name")[:1]

    # Get Opening Balance
    try:
        opening_balance = Account.objects.get(id=account).opening_balance
    except Account.DoesNotExist:
        opening_balance = 0

    # Get Archive Balance
    try:
        archive_balance = Account.objects.get(id=account).archive_balance
    except Account.DoesNotExist:
        archive_balance = 0

    all_transactions = None
    if not tags:
        # Get all non archived transactions less than end_date
        all_transactions = Transaction.objects.filter(
            Q(source_account_id=account) | Q(destination_account_id=account),
            transaction_date__lt=end_date,
        ).exclude(status_id=4)
    else:
        all_transactions = Transaction.objects.filter(
            add_date__range=[start_date, end_date],
            transactiondetail__tag_id__in=tags,
        ).order_by("-add_date", "-id")

    # Filter for transactions and source/destination for transfers
    if transfers_only:
        all_transactions = all_transactions.filter(
            transaction_type_id=3,
            source_account_id=transfer_ids[0],
            destination_account_id=transfer_ids[1],
            status_id=1,
        )

    # Annotate Source, Destination, Pretty Account Names if not totals_only
    if not totals_only:
        all_transactions = all_transactions.annotate(
            source_name=Coalesce(
                Subquery(source_account_name),
                Value("Unknown Account"),
            ),
            destination_name=Coalesce(
                Subquery(destination_account_name),
                Value("Unknown Account"),
            ),
        )
        all_transactions = all_transactions.annotate(
            pretty_account=Case(
                When(
                    transaction_type_id=3,
                    then=Concat(
                        F("source_name"),
                        Value(" => "),
                        F("destination_name"),
                    ),
                ),
                default=F("source_name"),
                output_field=CharField(),  # Correctly specify the output field
            )
        )

    # Annotate pretty total
    all_transactions = all_transactions.annotate(
        pretty_total=Case(
            When(
                transaction_type_id=2,
                then=Abs(F("total_amount")),
            ),
            When(
                transaction_type_id=1,
                then=-Abs(F("total_amount")),
            ),
            When(
                transaction_type_id=3,
                then=Case(
                    When(
                        source_account_id=account,
                        then=-Abs(F("total_amount")),
                    ),
                    default=Abs(F("total_amount")),
                    output_field=DecimalField(
                        max_digits=12, decimal_places=2
                    ),  # Ensure the correct output field
                ),
            ),
            default=Value(
                0,
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),  # Ensure the correct output field
            output_field=DecimalField(
                max_digits=12, decimal_places=2
            ),  # Ensure the correct output field
        )
    )

    # Get Cleared Transactions
    cleared_transactions = all_transactions.exclude(status_id=1)

    # Add custom sorting to Cleared Transactions
    cleared_transactions = cleared_transactions.annotate(
        custom_ordering=Case(
            When(status_id=1, then=Value(2)),
            When(status_id=2, then=Value(0)),
            When(status_id=3, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
    )

    # Annotate Cleared Transactions with balance
    cleared_transactions = cleared_transactions.annotate(
        cumulative_balance=Window(
            expression=Sum(F("pretty_total")),
            order_by=[
                "custom_ordering",
                "transaction_date",
                "-pretty_total",
                "-id",
            ],
        )
    )
    cleared_transactions = cleared_transactions.annotate(
        balance=ExpressionWrapper(
            F("cumulative_balance")
            + Value(opening_balance)
            + Value(archive_balance),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    )

    # Calculate cumulative balance up to to last cleared transaction
    cleared_balance = opening_balance + archive_balance
    if cleared_transactions:
        cleared_balance = (
            cleared_transactions.order_by(
                "custom_ordering", "transaction_date", "-pretty_total", "-id"
            )
            .last()
            .balance
        )

    # Add tags to cleared transactions if not totals_only
    if not totals_only:
        for transaction in cleared_transactions:
            transaction_details = TransactionDetail.objects.filter(
                transaction_id=transaction.id
            )
            if tags:
                transaction_details = transaction_details.filter(
                    tag_id__in=tags,
                )
                tag_sum = 0
                for detail in transaction_details:
                    tag_sum += detail.detail_amt
                transaction.tag_total = tag_sum
            details = list(transaction_details)
            tag_list = list(
                transaction_details.annotate(
                    parent_tag=F("tag__parent__tag_name"),
                    child_tag=F("tag__child__tag_name"),
                    tag_name_combined=Case(
                        When(child_tag__isnull=True, then=F("parent_tag")),
                        default=Concat(
                            F("parent_tag"), Value(" / "), F("child_tag")
                        ),
                        output_field=CharField(),
                    ),
                )
                .exclude(tag_name_combined__isnull=True)
                .values_list("tag_name_combined", flat=True)
            )
            transaction.tags = tag_list
            transaction.details = details

    # Create list from cleared transactions
    cleared_transactions_list = list(cleared_transactions)

    pending_transactions_list = []

    # Get pending transactions
    pending_transactions = all_transactions.filter(status_id=1)

    # Annotate pending transactions with balance
    pending_transactions = pending_transactions.annotate(
        balance=ExpressionWrapper(
            Value(cleared_balance),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    )

    # Add tags to pending transactions if not totals_only
    if not totals_only:
        for transaction in pending_transactions:
            transaction_details = TransactionDetail.objects.filter(
                transaction_id=transaction.id
            )
            if tags:
                transaction_details = transaction_details.filter(
                    tag_id__in=tags,
                )
                tag_sum = 0
                for detail in transaction_details:
                    tag_sum += detail.detail_amt
                transaction.tag_total = tag_sum
            details = list(transaction_details)
            tag_list = list(
                transaction_details.annotate(
                    parent_tag=F("tag__parent__tag_name"),
                    child_tag=F("tag__child__tag_name"),
                    tag_name_combined=Case(
                        When(child_tag__isnull=True, then=F("parent_tag")),
                        default=Concat(
                            F("parent_tag"), Value(" / "), F("child_tag")
                        ),
                        output_field=CharField(),
                    ),
                )
                .exclude(tag_name_combined__isnull=True)
                .values_list("tag_name_combined", flat=True)
            )
            transaction.tags = tag_list
            transaction.details = details

    # Create a list from pending_transactions
    pending_transactions_list = list(pending_transactions)

    reminder_transactions_list = []
    if not cleared_only:
        # Get a list of transactions based on reminders
        if transfers_only:
            reminder_transactions_list = get_reminder_transaction_list(
                end_date, 0, False, True, [transfer_ids[0], transfer_ids[1]]
            )
        else:
            reminder_transactions_list = get_reminder_transaction_list(
                end_date, account, forecast
            )

    # Combine pending and reminder transactions
    transactions_to_be_sorted = (
        pending_transactions_list + reminder_transactions_list
    )

    # Sort the list of transactions
    sorted_transactions = sort_transaction_list(transactions_to_be_sorted)

    # Add balances to sorted transactions
    sorted_transactions_with_balances = add_balances_to_transaction_list(
        sorted_transactions, cleared_balance
    )

    # Combine cleared transactions with sorted transactions with balances
    transactions = cleared_transactions_list + sorted_transactions_with_balances

    # Filter transactions for status and greater than start date, record previous balance
    if forecast:

        def get_transaction_date(transaction):
            # Check if the item is an object with an attribute 'transaction_date'
            if hasattr(transaction, "transaction_date"):
                return transaction.transaction_date
            # Check if the item is a dictionary with a 'transaction_date' key
            elif (
                isinstance(transaction, dict)
                and "transaction_date" in transaction
            ):
                return transaction["transaction_date"]
            # Return None if neither applies
            return None

        def filter_new_transactions(transactions, start_date):
            # Filter the transactions where transaction_date is greater than today
            return [
                transaction
                for transaction in transactions
                if get_transaction_date(transaction)
                and get_transaction_date(transaction) >= start_date
            ]

        def filter_previous_transactions(transactions, start_date):
            # Filter the transactions where transaction_date is greater than today
            return [
                transaction
                for transaction in transactions
                if get_transaction_date(transaction)
                and get_transaction_date(transaction) < start_date
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
        return filtered_transactions, previous_balance
    else:
        return transactions, Decimal(0.00)
