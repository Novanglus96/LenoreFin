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
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


def calculate_cc_bill(
    account_id: int,
    transactions: List[TransactionOut],
    start_date: date,
    end_date: date,
    funding: bool,
) -> List[TransactionOut]:
    """
    The function `calculate_cc_bill` calculates the payments and interest for cc accounts and adds
    them as forecast transactions.

    Args:
        account_id (int): The ID of an account to calcuate credit card paymentes for.
        transactions (List[FullTransaction]): a list of transactions for this account
        start_date (date): The start date for this window of time to create transactions for.
        end_date (date): The end date for this window of time to create transacitons for.
        funding (bool): True if this is being calculated for the funding account.
    Returns:
        (List[FullTransaction]): List of Interest and Payment transcations.
    """

    # Setup variables
    if funding:
        multiplier = -1
    else:
        multiplier = 1

    account = Account.objects.get(id=account_id)
    added_transactions = []
    if account.account_type.id == 1 and account.calculate_payments:
        due_date = account.due_date
        next_cycle_date = account.next_cycle_date
        statement_cycle_length = account.statement_cycle_length
        statement_cycle_period = account.statement_cycle_period
        funding_account = account.funding_account
        annual_rate = account.annual_rate
        payment_strategy = account.payment_strategy
        payment_amount = account.payment_amount
        minimum_payment_amount = account.minimum_payment_amount
        today = get_todays_date_timezone_adjusted()
        temp_id = -10001
        status = TransactionStatus.objects.get(id=1)
        transaction_type_transfer = TransactionType.objects.get(id=3)
        transaction_type_expense = TransactionType.objects.get(id=1)
        interest_calculations = account.calculate_interest

        # Get statement cycles
        statement_cycles = generate_statement_cycles(
            next_cycle_date,
            due_date,
            end_date,
            statement_cycle_length,
            statement_cycle_period,
            transactions,
        )

        # Calculate statement transactions
        total_credits = Decimal(0.00)
        total_debits = Decimal(0.00)
        total_payments = Decimal(0.00)
        total_interest = Decimal(0.00)
        x = 0
        for cycle in statement_cycles:
            total_credits += cycle["statement_credits"]
            total_debits += cycle["statement_debits"]
            cycle_balance = Decimal(0.00)
            cycle_interest = Decimal(0.00)
            cycle_balance = (
                total_credits + total_debits + total_interest + total_payments
            )
            cycle_payment = Decimal(0.00)
            # Calculate Interest
            if x > 0 and interest_calculations:
                # If we are past due date, calculate interest
                if statement_cycles[0]["statement_due"] < today:
                    if cycle_balance != cycle["statement_debits"]:
                        unpaid = cycle_balance - cycle["statement_debits"]
                        cycle_interest = calculate_interest(
                            unpaid,
                            annual_rate,
                            statement_cycles[x - 1]["statement_end"],
                            cycle["statement_end"],
                        )
                        total_interest += cycle_interest
                        # Create Inteterest Transaction
                        if (
                            cycle["statement_end"] > today
                            and cycle_interest < 0
                            and not funding
                        ):
                            interest_transaction = TransactionOut.model_validate(
                                {
                                    "id": temp_id,
                                    "transaction_date": cycle["statement_end"],
                                    "total_amount": cycle_interest,
                                    "status": status,
                                    "memo": "Interest Charge",
                                    "description": f"({account.account_name} Estimated Interest)",
                                    "edit_date": today,
                                    "add_date": today,
                                    "transaction_type": transaction_type_expense,
                                    "pretty_total": -abs(cycle_interest),
                                    "pretty_account": account.account_name,
                                    "source_account_id": account_id,
                                    "destination_account_id": None,
                                    "balance": 0.00,
                                    "tags": ["Interest"],
                                    "reminder_id": None,
                                    "simulated": True,
                                }
                            )
                            added_transactions.append(interest_transaction)
                            temp_id -= 1
            # Calculate Payment
            if x > 0:
                if cycle_balance < 0:
                    if payment_strategy == "F":
                        cycle_payment = abs(cycle_balance) + abs(cycle_interest)
                    elif payment_strategy == "M":
                        if (
                            abs(cycle_balance) + abs(cycle_interest)
                            >= minimum_payment_amount
                        ):
                            cycle_payment = minimum_payment_amount
                        else:
                            cycle_payment = abs(cycle_balance) + abs(
                                cycle_interest
                            )
                    elif payment_strategy == "C":
                        if (
                            abs(cycle_balance) + abs(cycle_interest)
                            >= payment_amount
                        ):
                            cycle_payment = payment_amount
                        else:
                            cycle_payment = abs(cycle_balance) + abs(
                                cycle_interest
                            )
                    if cycle["statement_due"] > today:
                        payment_transaction = TransactionOut.model_validate(
                            {
                                "id": temp_id,
                                "transaction_date": cycle["statement_due"],
                                "total_amount": abs(cycle_payment),
                                "status": status,
                                "memo": None,
                                "description": f"({account.account_name} Estimated Payment)",
                                "edit_date": today,
                                "add_date": today,
                                "transaction_type": transaction_type_transfer,
                                "paycheck": None,
                                "checkNumber": None,
                                "pretty_total": abs(cycle_payment) * multiplier,
                                "pretty_account": f"{funding_account.account_name} => {account.account_name}",
                                "source_account_id": funding_account.id,
                                "destination_account_id": account_id,
                                "balance": 0.00,
                                "tags": ["Credit Card", "Transfer"],
                                "reminder_id": None,
                                "simulated": True,
                            }
                        )
                        added_transactions.append(payment_transaction)
                        total_payments += cycle_payment
                        temp_id -= 1
            x += 1

    return added_transactions


def increment_date(incr_date: date, period: str, length: int):
    """
    The function `increment_date` increments a given date by the provided length
    and period.

    Args:
        incr_date (date): The date to increment.
        period (str): d = week, w = week, m = month, y = year.
        length (int): Length of the period.

    Returns:
        (date): Returns the new date
    """
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


def generate_statement_cycles(
    last_statement_end_date: date,
    last_statment_due_date: date,
    forecast_end_date: date,
    statement_cycle_length: int,
    statement_cycle_period: str,
    transactions: List[TransactionOut],
):
    """
    The function `generate_statement_cycle` generates a list of dictionaries of statement
    information.

    Args:
        last_statement_end_date (date): Last statement end date.
        last_statment_due_date (date): Last statement due date.
        forecast_end_date (date): Forecast end date.
        statement_cycle_length (int): Statement cycle length.
        statement_cycle_period (str): Statement cycle period.
        transactions (List[TransactionOut]): Transactions for the account for the forecast
        period.

    Returns:
        (List[dict]): A list of dictionaries of statement information
    """
    statement_cycles = []
    statement_start = increment_date(
        last_statement_end_date,
        statement_cycle_period,
        -(statement_cycle_length),
    )
    statement_due = increment_date(last_statment_due_date, "m", -1)
    while statement_start <= forecast_end_date:
        statement_end = increment_date(
            statement_start, statement_cycle_period, statement_cycle_length
        )

        statement_due = increment_date(statement_due, "m", 1)
        statement_credits = sum(
            tx.pretty_total
            for tx in transactions
            if (statement_start < tx.transaction_date <= statement_end)
            and tx.pretty_total > 0
        )
        statement_debits = sum(
            tx.pretty_total
            for tx in transactions
            if (statement_start < tx.transaction_date <= statement_end)
            and tx.pretty_total < 0
        )

        statement_cycles.append(
            {
                "statement_start": statement_start,
                "statement_end": statement_end,
                "statement_due": statement_due,
                "statement_credits": statement_credits,
                "statement_debits": statement_debits,
            }
        )
        statement_start = statement_end

    return statement_cycles


def calculate_interest(
    amount: Decimal, annual_rate: Decimal, start_date: date, end_date: date
):
    """
    The function `calculate_interest` generates the amount of interest for an amount, given
    an annual_rate and a start and end date.

    Args:
        amount (Decimal): The amount to generate interest for.
        annual_rate (Decimal): The APR for the account.
        start_date (date): The start date to generate interest.
        end_date (date): The end date to generate interest.

    Returns:
        (List[dict]): A list of dictionaries of statement information
    """
    interest = Decimal(0.00)
    delta = end_date - start_date
    days = delta.days
    daily_rate = annual_rate / 365 / 100
    interest = amount * daily_rate * days
    return interest.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
