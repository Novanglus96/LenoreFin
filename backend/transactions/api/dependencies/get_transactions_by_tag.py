from typing import List
from datetime import date
from transactions.api.schemas.transaction import TransactionOut
from transactions.models import Transaction, TransactionDetail
from transactions.api.dependencies.transaction_utilities import (
    annotate_transaction_display_info,
    annotate_transaction_total,
    sort_transactions,
    sort_transaction_list,
    add_tag_totals,
)
from django.db.models import (
    Case,
    When,
    Value,
    F,
    CharField,
)
from django.db.models.functions import Concat


def get_transactions_by_tag(
    end_date: date,
    totals_only: bool,
    start_date: date,
    tags: List[int],
    cleared_only: bool,
) -> List[TransactionOut]:
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
    # Setup Variables
    pending_transactions_list = []
    cleared_transactions_list = []
    sorted_transactions_list = []

    # Get tag transactions
    transactions = Transaction.objects.filter(
        add_date__range=[start_date, end_date],
        transactiondetail__tag_id__in=tags,
    ).order_by("-add_date", "-id")

    # Annotate transactions details
    if not totals_only:
        transactions = annotate_transaction_display_info(transactions)

    # Annotate transaction pretty total
    transactions = annotate_transaction_total(transactions)

    # Filter for cleared transactions
    cleared_transactions = transactions.exclude(status_id__in=[1, 4])

    # Sort Cleared Transactions
    cleared_transactions = sort_transactions(cleared_transactions, True)

    # Create List of Cleared Transactions
    cleared_transactions_list = [
        TransactionOut.from_orm(obj) for obj in cleared_transactions
    ]

    # Add tag totals to Cleared transactions
    cleared_transactions_list = add_tag_totals(cleared_transactions_list, tags)

    # Filter for Pending transactions
    pending_transactions = transactions.exclude(status_id__in=[2, 3, 4])

    # Create list of Pending TransactionOut objects
    pending_transactions_list = [
        TransactionOut.from_orm(obj) for obj in pending_transactions
    ]

    # Add tag totals to Pending transactions
    pending_transactions_list = add_tag_totals(pending_transactions_list, tags)

    # Sort Pending Transactions
    pending_transactions_list = sort_transaction_list(pending_transactions_list)

    # Create sorted list
    sorted_transactions_list = (
        cleared_transactions_list + pending_transactions_list
    )

    # Add tags to transactions
    if not totals_only:
        for transaction in sorted_transactions_list:
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

    if cleared_only:
        return cleared_transactions_list
    else:
        return sorted_transactions_list
