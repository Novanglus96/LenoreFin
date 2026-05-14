from transactions.models import (
    Transaction,
    TransactionDetail,
    ReminderCacheTransactionDetail,
    ForecastCacheTransactionDetail,
)
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
    Count,
)
from django.db.models.functions import Concat, Coalesce
from accounts.models import Account
from django.db.models.functions import Abs
from decimal import Decimal
from typing import List, Optional
from transactions.api.schemas.transaction import TransactionOut


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
                transaction_type__slug='transfer',
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
    if transactions.model is Transaction:
        all_transactions = all_transactions.annotate(
            attachment_count=Count("transactionimage", distinct=True)
        )
    else:
        all_transactions = all_transactions.annotate(
            attachment_count=Value(0, output_field=IntegerField())
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
                transaction_type__slug='income',
                then=Abs(F("total_amount")),
            ),
            When(
                transaction_type__slug='expense',
                then=-Abs(F("total_amount")),
            ),
            When(
                transaction_type__slug='transfer',
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


def annotate_transaction_total_for_parent(
    transactions: QuerySet,
    child_ids: list,
) -> QuerySet:
    """
    Like annotate_transaction_total but for a combined parent account view.
    Transfers where the child account is the source are negative; destination is positive.
    Internal transfers (both sides are children) must be excluded before calling this.
    """
    if not isinstance(transactions, QuerySet):
        raise TypeError("Expected a QuerySet")

    all_transactions = transactions.annotate(
        pretty_total=Case(
            When(transaction_type__slug='income', then=Abs(F("total_amount"))),
            When(transaction_type__slug='expense', then=-Abs(F("total_amount"))),
            When(
                transaction_type__slug='transfer',
                source_account_id__in=child_ids,
                then=-Abs(F("total_amount")),
            ),
            When(
                transaction_type__slug='transfer',
                destination_account_id__in=child_ids,
                then=Abs(F("total_amount")),
            ),
            default=Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)),
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
                When(status__slug='pending', then=Value(2)),
                When(status__slug='cleared', then=Value(0)),
                When(status__slug='reconciled', then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by("custom_order", "transaction_date", "-pretty_total", "-id")
    else:
        transactions = transactions.annotate(
            custom_order=Case(
                When(status__slug='pending', then=Value(2)),
                When(status__slug='cleared', then=Value(0)),
                When(status__slug='reconciled', then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by(
            "-custom_order",
            "-transaction_date",
            "pretty_total",
            "id",
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
    transactions: QuerySet, type: str = "t"
) -> QuerySet:
    """
    add_tags_to_transactions _summary_

    _extended_summary_
    """
    transaction_list = list(transactions)
    if not transaction_list:
        return transactions

    txn_ids = [t.id for t in transaction_list]

    if type == "t":
        detail_model = TransactionDetail
    elif type == "r":
        detail_model = ReminderCacheTransactionDetail
    else:
        detail_model = ForecastCacheTransactionDetail

    all_details = list(
        detail_model.objects.filter(transaction_id__in=txn_ids)
        .select_related("transaction", "tag")
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
    )

    details_by_txn: dict = {}
    tags_by_txn: dict = {}
    for detail in all_details:
        tid = detail.transaction_id
        details_by_txn.setdefault(tid, []).append(detail)
        if detail.tag_name_combined:
            tags_by_txn.setdefault(tid, []).append(detail.tag_name_combined)

    for transaction in transaction_list:
        transaction.tags = tags_by_txn.get(transaction.id, [])
        transaction.details = details_by_txn.get(transaction.id, [])

    return transaction_list


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
            status_slug = (
                transaction["status"].slug if transaction["status"] else None
            )
        else:
            status_slug = transaction.status.slug if transaction.status else None

        if status_slug == 'pending':
            return 2
        elif status_slug in ['cleared', 'reconciled']:
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
