from decimal import Decimal
from typing import List, Optional, Dict, Any


def add_balances_to_transaction_list(
    transactions: List[Any], start_balance: Decimal
) -> List[Any]:
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
