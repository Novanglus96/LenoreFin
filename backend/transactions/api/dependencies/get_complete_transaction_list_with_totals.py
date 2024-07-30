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


def get_complete_transaction_list_with_totals(
    end_date: date,
    account: int,
    totals_only: bool,
    forecast: Optional[bool] = False,
    start_date: Optional[date] = None,
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
    opening_balance = Account.objects.get(id=account).opening_balance

    # Get all transactions less than end_date
    all_transactions = Transaction.objects.filter(
        Q(source_account_id=account) | Q(destination_account_id=account),
        transaction_date__lt=end_date,
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

    # Get Past Transactions
    past_transactions = all_transactions.filter(transaction_date__lt=today)

    # Annotate Past Transactions with balance
    past_transactions = past_transactions.annotate(
        cumulative_balance=Window(
            expression=Sum(F("pretty_total")),
            order_by=[
                Case(
                    When(status_id=1, then=Value(2)),
                    When(status_id=2, then=Value(0)),
                    When(status_id=3, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                ),
                "transaction_date",
                "-pretty_total",
                "-id",
            ],
        )
    )
    past_transactions = past_transactions.annotate(
        balance=ExpressionWrapper(
            F("cumulative_balance") + Value(opening_balance),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    )

    # Calculate cumulative balance up to to today
    cumulative_balance_up_to_today = opening_balance
    if past_transactions:
        cumulative_balance_up_to_today = (
            past_transactions.last().cumulative_balance
        )

    # Add tags to past transactions if not totals_only
    if not totals_only:
        for transaction in past_transactions:
            tags = list(
                TransactionDetail.objects.filter(transaction_id=transaction.id)
                .annotate(
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
            transaction.tags = tags

    # Create list from past transactions
    past_transactions_list = list(past_transactions)

    # Get future transactions
    future_transactions = all_transactions.filter(transaction_date__gte=today)

    # Annotate future transactions with balance
    future_transactions = future_transactions.annotate(
        balance=ExpressionWrapper(
            Value(cumulative_balance_up_to_today),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    )

    # Add tags to future transactions if not totals_only
    if not totals_only:
        for transaction in future_transactions:
            tags = list(
                TransactionDetail.objects.filter(transaction_id=transaction.id)
                .annotate(
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
            transaction.tags = tags

    # Create a list from future_transactions
    future_transactions_list = list(future_transactions)

    # Get a list of transactions based on reminders
    reminder_transactions_list = get_reminder_transaction_list(
        end_date, account, forecast
    )

    # Combine future and reminder transactions
    transactions_to_be_sorted = (
        future_transactions_list + reminder_transactions_list
    )

    # Sort the list of transactions
    sorted_transactions = sort_transaction_list(transactions_to_be_sorted)

    # Add balances to sorted transactions
    sorted_transactions_with_balances = add_balances_to_transaction_list(
        sorted_transactions, cumulative_balance_up_to_today
    )

    # Combine past transactions with sorted transactions with balances
    transactions = past_transactions_list + sorted_transactions_with_balances

    # Filter transactions for status and greater than start date, record previous balance
    if forecast:
        filtered_transactions = []
        last_index = -1
        previous_balance = opening_balance
        if start_date:
            start = start_date
        else:
            start = today
        for index, transaction in enumerate(transactions):
            if isinstance(transaction, dict):
                if transaction["transaction_date"] >= start:
                    if start == today:
                        if transaction["status"].id == 1:
                            filtered_transactions.append(transaction)
                    else:
                        filtered_transactions.append(transaction)
                    if last_index == -1:
                        last_index = index
            else:
                if transaction.transaction_date >= start:
                    if start == today:
                        if transaction.status.id == 1:
                            filtered_transactions.append(transaction)
                    else:
                        filtered_transactions.append(transaction)
                    if last_index == -1:
                        last_index = index
        if last_index != -1:
            if last_index > 0:
                if isinstance(
                    transactions[last_index - 1],
                    dict,
                ):
                    previous_balance = transactions[last_index - 1]["balance"]
                else:
                    previous_balance = transactions[last_index - 1].balance
            elif last_index == 0 and start == today:
                if isinstance(
                    transactions[last_index - 1],
                    dict,
                ):
                    previous_balance = transactions[last_index - 1]["balance"]
                else:
                    previous_balance = transactions[last_index - 1].balance
        return filtered_transactions, previous_balance
    else:
        return transactions, Decimal(0.00)
