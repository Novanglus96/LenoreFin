from transactions.models import Transaction, TransactionDetail
from django.db.models.query import QuerySet
from django.db.models import (
    Case,
    When,
    Value,
    F,
    CharField,
    Subquery,
    OuterRef,
    DecimalField,
    IntegerField,
    Window,
    Sum,
    ExpressionWrapper,
    Q,
)
from django.db.models.functions import Concat, Coalesce
from accounts.models import Account
from django.db.models.functions import Abs
from decimal import Decimal
from typing import List, Tuple, Optional
from transactions.api.schemas.transaction import TransactionOut
from datetime import date


def annotate_transaction_display_info(
    transactions: QuerySet[Transaction],
) -> QuerySet[Transaction]:
    """
    `annotate_transaction_display_info` annotates a given transaction queryset
    with pretty names for Source Account, Destination Account and Pretty Name.

    Args:
        transactions (QuerySet[Transaction]): A queryset of Transaction objects.

    Returns:
        (QuerySet[Transaction]): An annotated queryset of Transaction objects.
    """
    # Check we received a QuerySet
    if not isinstance(transactions, QuerySet):
        raise TypeError("Expected a QuerySet")

    # Subqueries
    source_account_name = Account.objects.filter(
        id=OuterRef("source_account_id")
    ).values("account_name")[:1]
    destination_account_name = Account.objects.filter(
        id=OuterRef("destination_account_id")
    ).values("account_name")[:1]

    # Annotate Source, Destination, Pretty Account Names
    all_transactions = transactions.annotate(
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
            output_field=CharField(),
        )
    )
    return all_transactions


def annotate_transaction_total(
    transactions: QuerySet[Transaction], account_id: Optional[int] = 0
) -> QuerySet[Transaction]:
    """
    annotate_transaction_total

    _extended_summary_
    """
    # Check we received a QuerySet
    if not isinstance(transactions, QuerySet):
        raise TypeError("Expected a QuerySet")

    # Annotate pretty total
    all_transactions = transactions.annotate(
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
                        source_account_id=account_id,
                        then=-Abs(F("total_amount")),
                    ),
                    default=Abs(F("total_amount")),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
            ),
            default=Value(
                0,
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    )
    return all_transactions


def sort_transactions(
    transactions: QuerySet[Transaction],
    asc: bool = True,
) -> QuerySet[Transaction]:
    """
    The function `sort_transactions` returns the provided transactions sorted.

    Args:
        transactions (QuerySet[Transaction]): A list of transactions to sort
        asc (bool): Perform a full (all objects) sort order update
    Returns:
        QuerySet[Transaction]: Sorted QuerySet of Transaction objects.
    """
    if asc:
        transactions = transactions.annotate(
            custom_order=Case(
                When(status_id=1, then=Value(2)),
                When(status_id=2, then=Value(0)),
                When(status_id=3, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by(
            "custom_order",
            "transaction_date",
            "-total_amount",
            "id",
        )
    else:
        transactions = transactions.annotate(
            custom_order=Case(
                When(status_id=1, then=Value(2)),
                When(status_id=2, then=Value(0)),
                When(status_id=3, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by(
            "-custom_order",
            "-transaction_date",
            "total_amount",
            "-id",
        )

    return transactions


def annotate_transaction_balance(
    transactions: QuerySet[Transaction],
    opening_balance: Decimal,
    archive_balance: Decimal,
) -> QuerySet[Transaction]:
    """
    `annotate_transaction_balance` annotates a queryset of Transaction objects
    with totals

    Args:
        transactions (QuerySet[Transaction]): A quertyset of transactions to annotate
        opening_balance (Decimal): Opening balance of the account.
        archive_balance (Decimal): Archive balance of the account.
    Returns:
        QuerySet[Transaction]: Annotated QuerySet of Transaction objects.
    """
    # Annotate transactions with balance
    annotated_transactions = transactions.annotate(
        cumulative_balance=Window(
            expression=Sum(F("pretty_total")),
            order_by=[
                "custom_order",
                "transaction_date",
                "-pretty_total",
                "-id",
            ],
        )
    )
    annotated_transactions = annotated_transactions.annotate(
        balance=ExpressionWrapper(
            F("cumulative_balance")
            + Value(opening_balance)
            + Value(archive_balance),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    )
    return annotated_transactions


def add_tags_to_transactions(
    transactions: QuerySet[Transaction],
) -> QuerySet[Transaction]:
    """
    add_tags_to_transactions _summary_

    _extended_summary_
    """
    # Add tags to transactions
    for transaction in transactions:
        transaction_details = TransactionDetail.objects.filter(
            transaction_id=transaction.id
        )
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
    return transactions


def sort_transaction_list(
    transactions: List[TransactionOut],
) -> List[TransactionOut]:
    """
    The function `sort_transaction_list` sorts a provided list of
    transactions.

    Args:

    Returns:
        transactions: List of sorted transactions
    """

    # Helper function to sort by status
    def get_status_id(transaction):
        if isinstance(transaction, dict):
            return (
                transaction["status"].id
                if transaction["status"]
                else float("inf")
            )
        else:
            return transaction.status.id if transaction.status else float("inf")

    # Helper function to sort by priority
    def get_priority(transaction):
        if isinstance(transaction, dict):
            status_id = (
                transaction["status"].id if transaction["status"] else None
            )
        else:
            status_id = transaction.status.id if transaction.status else None

        if status_id == 1:
            return 2
        elif status_id in [2, 3]:
            return 0
        else:
            return 1

    # Helper function to sort by transaction date
    def get_transaction_date(transaction):
        if isinstance(transaction, dict):
            return transaction["transaction_date"]
        else:
            return transaction.transaction_date

    # Helper function to sort by pretty total
    def get_pretty_total(transaction):
        if isinstance(transaction, dict):
            return transaction.get("pretty_total", 0)
        else:
            return transaction.pretty_total

    # Helper function to sort by id
    def get_id(transaction):
        if isinstance(transaction, dict):
            return transaction.get("id", 0)
        else:
            return transaction.id

    # Sort transactions
    sorted_transactions = sorted(
        transactions,
        key=lambda t: (
            get_priority(t),
            get_status_id(t),
            get_transaction_date(t),
            -get_pretty_total(t),
            -get_id(t),
        ),
    )

    return sorted_transactions


def add_balances_to_transaction_list(
    transactions: List[TransactionOut], start_balance: Decimal
) -> List[TransactionOut]:
    """
    The function `add_balances_to_transaction_list` adds balances
    to a list of transactions and returns the list

    Args:
        transactions (List): A list of transactions to update.
        start_balance (Decimal): The starting balance.

    Returns:
        transactions: List of transactions with balances
    """

    # Setup variables
    running_total = start_balance

    # Calculate and add balances
    for transaction in transactions:
        if isinstance(transaction, dict):
            running_total += transaction["pretty_total"]
            transaction["balance"] = running_total
        else:
            running_total += transaction.pretty_total
            transaction.balance = running_total

    return transactions


def get_transactions_list(
    account_id: int,
    end_date: date,
    totals_only: bool,
    opening_balance: Decimal,
    archive_balance: Decimal,
    cleared: bool,
) -> Tuple[List[TransactionOut], Decimal]:
    """
    The function `add_balances_to_transaction_list` adds balances
    to a list of transactions and returns the list

    Args:
        transactions (List): A list of transactions to update.
        start_balance (Decimal): The starting balance.

    Returns:
        transactions: List of transactions with balances
    """
    # Set Status IDs
    if cleared:  # Exclude archived and pending
        status_ids = [1, 4]
    else:  # Exclude Archived, Cleared, and Reconciled
        status_ids = [2, 3, 4]
    # Get transactions less then end date
    transactions = Transaction.objects.filter(
        Q(source_account_id=account_id) | Q(destination_account_id=account_id),
        transaction_date__lt=end_date,
    ).exclude(status_id__in=status_ids)

    # If not totals only, annotate transactions with pretty information
    if not totals_only:
        transactions = annotate_transaction_display_info(transactions)

    # Annotate pretty totals
    transactions = annotate_transaction_total(transactions, account_id)

    if cleared:
        # Add custom sorting to Transactions
        transactions = sort_transactions(transactions, True)

        # Annotate Transactions with balance
        transactions = annotate_transaction_balance(
            transactions, opening_balance, archive_balance
        )

        # Calculate cumulative balance
        balance = opening_balance + archive_balance
        if transactions:
            balance = (
                transactions.order_by(
                    "custom_order", "transaction_date", "-pretty_total", "-id"
                )
                .last()
                .balance
            )
    else:
        balance = 0

    # Add tags to cleared transactions if not totals_only
    if not totals_only:
        transactions = add_tags_to_transactions(transactions)

    # Create list of cleared TransactionOut objects
    transactions_list = [TransactionOut.from_orm(obj) for obj in transactions]

    return transactions_list, balance


def add_tag_totals(
    transactions: List[TransactionOut], tags: List[int]
) -> List[TransactionOut]:
    """
    The function `add_balances_to_transaction_list` adds balances
    to a list of transactions and returns the list

    Args:
        transactions (List): A list of transactions to update.
        start_balance (Decimal): The starting balance.

    Returns:
        transactions: List of transactions with balances
    """
    for transaction in transactions:
        transaction_details = TransactionDetail.objects.filter(
            transaction_id=transaction.id
        )
        transaction_details = transaction_details.filter(tag_id__in=tags)
        tag_sum = 0
        for detail in transaction_details:
            tag_sum += detail.detail_amt
        transaction.tag_total = tag_sum

    return transactions
