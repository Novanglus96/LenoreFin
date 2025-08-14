from typing import List
from transactions.api.schemas.transaction import TransactionOut
from transactions.models import (
    TransactionType,
    TransactionStatus,
)
from accounts.models import Account
from administration.api.dependencies.get_todays_date_timezone_adjusted import (
    get_todays_date_timezone_adjusted,
)
from dateutil.relativedelta import relativedelta


def calculate_cc_bill(
    account_id: int,
    transactions: List[TransactionOut],
    cleared_transactions: List[TransactionOut],
    start_date,
    end_date,
    funding: bool,
) -> List[TransactionOut]:
    """
    The function `calculate_cc_bill` calculates the payments for cc accounts and adds
    them as forecast transactions.

    Args:
        account (int): The ID of an account to calcuate credit card paymentes for.
        transactions (List[FullTransaction]): a list of transactions for this account
        start_date (date): The start date for this window of time to create transactions for.
        end_date (date): The end date for this window of time to create transacitons for.
    Returns:
        (List[FullTransaction]): List of transactions including the statement forecast transactions.
    """

    def increment_date(incr_date, period: str, length: int):
        if period == "d":
            return incr_date + relativedelta(days=length)
        elif period == "w":
            return incr_date + relativedelta(weeks=length)
        elif period == "m":
            return incr_date + relativedelta(months=length)
        elif period == "y":
            return incr_date + relativedelta(years=length)
        else:
            raise ValueError(f"Unsupported period: {period}")

    # Setup variables
    today = get_todays_date_timezone_adjusted()
    combined_transactions = transactions + cleared_transactions
    if funding:
        multiplier = -1
    else:
        multiplier = 1

    account = Account.objects.get(id=account_id)
    temp_id = -10001
    added_transactions = []
    results = []
    if account.account_type.id == 1 and account.calculate_payments:
        due_date = account.due_date
        next_cycle_date = account.next_cycle_date
        statement_cycle_length = account.statement_cycle_length
        statement_cycle_period = account.statement_cycle_period
        funding_account = account.funding_account
        status = TransactionStatus.objects.get(id=1)
        transaction_type = TransactionType.objects.get(id=3)
        tags = []

        current_start = increment_date(
            next_cycle_date, statement_cycle_period, -(statement_cycle_length)
        )
        current_due_date = increment_date(due_date, "m", -1)

        while current_start <= end_date:
            current_end = increment_date(
                current_start, statement_cycle_period, statement_cycle_length
            )

            current_due_date = increment_date(current_due_date, "m", 1)

            cycle_total = sum(
                tx.pretty_total
                for tx in combined_transactions
                if current_start <= tx.transaction_date < current_end
            )
            if cycle_total < 0:
                results.append(
                    {
                        "statement_start": current_start,
                        "statement_end": current_end,
                        "total_amount": cycle_total,
                        "due_date": current_due_date,
                    }
                )
            current_start = current_end
        for result in results:
            new_transaction = TransactionOut.model_validate(
                {
                    "id": temp_id,
                    "transaction_date": result["due_date"],
                    "total_amount": abs(result["total_amount"]),
                    "status": status,
                    "memo": None,
                    "description": f"{account.account_name} Payment",
                    "edit_date": today,
                    "add_date": today,
                    "transaction_type": transaction_type,
                    "paycheck": None,
                    "checkNumber": None,
                    "pretty_total": abs(result["total_amount"]) * multiplier,
                    "pretty_account": f"{funding_account.account_name} => {account.account_name}",
                    "source_account_id": funding_account.id,
                    "destination_account_id": account.id,
                    "balance": 0.00,
                    "tags": tags,
                    "reminder_id": None,
                    "simulated": True,
                }
            )
            added_transactions.append(new_transaction)
            temp_id -= 1
    return added_transactions
