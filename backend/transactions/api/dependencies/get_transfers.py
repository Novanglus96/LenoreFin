from typing import List
from datetime import date
from transactions.api.schemas.transaction import TransactionOut
from transactions.models import Transaction
from django.db.models import (
    Q,
)
from transactions.api.dependencies.transaction_utilities import (
    annotate_transaction_display_info,
    annotate_transaction_total,
    sort_transaction_list,
    add_tags_to_transactions,
)


def get_transfers(
    end_date: date,
    account_id: int,
    start_date: date,
    transfer_ids: List[int],
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
    # Get all related transactions
    all_transactions = Transaction.objects.filter(
        Q(source_account_id=account_id) | Q(destination_account_id=account_id),
        transaction_date__lt=end_date,
    ).exclude(status_id=4)

    # Filter for transactions and source/destination for transfers
    transfers = all_transactions.filter(
        transaction_type_id=3,
        source_account_id=transfer_ids[0],
        destination_account_id=transfer_ids[1],
        status_id=1,
    )

    # Annotate transfers with details
    transfers = annotate_transaction_display_info(transfers)

    # Annotate transfers with pretty totals
    transfers = annotate_transaction_total(transfers, account_id)

    # Add tags to transfers
    transfers = add_tags_to_transactions(transfers)

    # Create list of TransactionOut objects
    transfers_list = [TransactionOut.from_orm(obj) for obj in transfers]

    # Sort List
    transfers_list = sort_transaction_list(transfers_list)

    return transfers_list
