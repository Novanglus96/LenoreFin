from datetime import date
from typing import List, Optional, Tuple
from transactions.api.schemas.transaction import TransactionOut
from accounts.models import Account
from administration.api.dependencies.get_todays_date_timezone_adjusted import (
    get_todays_date_timezone_adjusted,
)
from transactions.api.dependencies.transaction_utilities import (
    sort_transaction_list,
    add_balances_to_transaction_list,
    get_transactions_list,
)
from transactions.api.dependencies.get_reminder_transaction_list import (
    get_reminder_transaction_list,
)
from transactions.api.dependencies.calculate_cc_bill import calculate_cc_bill
from decimal import Decimal


def get_transactions_by_account(
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
    # Setup variables
    today = get_todays_date_timezone_adjusted()
    cleared_transactions_list = []
    pending_transactions_list = []
    reminder_transactions_list = []
    cc_transactions_list = []
    cc_payment_accounts_transactions_list = []

    # Check if account exists.  Return an empty list if not.
    try:
        account = Account.objects.get(id=account_id)
    except Account.DoesNotExist:
        return [], Decimal(0.00)

    # Get Account Info
    opening_balance = account.opening_balance
    archive_balance = account.archive_balance
    cc_payment_accounts = Account.objects.filter(funding_account_id=account_id)

    # Get cleared transactions and cleared balance
    cleared_transactions_list, cleared_balance = get_transactions_list(
        account_id,
        end_date,
        totals_only,
        opening_balance,
        archive_balance,
        True,
    )

    # Get pending transactions
    pending_transactions_list, pending_balance = get_transactions_list(
        account_id,
        end_date,
        totals_only,
        opening_balance,
        archive_balance,
        False,
    )

    # Get reminder transactions
    if not cleared_only:
        reminder_transactions_list = get_reminder_transaction_list(
            end_date, account, forecast
        )

    # Combine pending and reminder transactions
    transactions_to_be_sorted = (
        pending_transactions_list + reminder_transactions_list
    )

    # Add CC forecast transactions
    cc_transactions_list = calculate_cc_bill(
        account_id,
        transactions_to_be_sorted,
        cleared_transactions_list,
        start_date,
        end_date,
        False,
    )

    # Add CC funding transactions
    if cc_payment_accounts:
        for payment_account in cc_payment_accounts:
            # Get cleared transactions and cleared balance
            (
                cleared_payment_account_transactions_list,
                cleared_payment_account_balance,
            ) = get_transactions_list(
                payment_account.id,
                end_date,
                totals_only,
                payment_account.opening_balance,
                payment_account.archive_balance,
                True,
            )
            # Get pending transactions
            (
                pending_payment_account_transactions_list,
                pending_payment_account_balance,
            ) = get_transactions_list(
                payment_account.id,
                end_date,
                totals_only,
                payment_account.opening_balance,
                payment_account.archive_balance,
                False,
            )
            # Get reminder transactions
            if not cleared_only:
                payment_account_reminder_transactions_list = (
                    get_reminder_transaction_list(
                        end_date, payment_account.id, forecast
                    )
                )

            # Combine pending and reminder transactions
            payment_account_transactions_to_be_sorted_list = (
                pending_payment_account_transactions_list
                + payment_account_reminder_transactions_list
            )
            payment_account_list = calculate_cc_bill(
                payment_account.id,
                payment_account_transactions_to_be_sorted_list,
                cleared_payment_account_transactions_list,
                start_date,
                end_date,
                True,
            )
            cc_payment_accounts_transactions_list += payment_account_list

    # Add cc transactions to transactions to be sorted
    transactions_to_be_sorted = (
        transactions_to_be_sorted
        + cc_transactions_list
        + cc_payment_accounts_transactions_list
    )

    # Sort transactions
    sorted_transactions = sort_transaction_list(transactions_to_be_sorted)

    # Add balances to sorted transactions
    sorted_transactions_with_balances = add_balances_to_transaction_list(
        sorted_transactions, cleared_balance
    )

    # Combine cleared transactions with sorted transactions with balances
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
        return filtered_transactions, previous_balance
    else:
        return transactions, Decimal(0.00)
