from decimal import Decimal
from typing import List, Optional, Dict, Any


def sort_transaction_list(transactions: List[Any]) -> List[Any]:
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
