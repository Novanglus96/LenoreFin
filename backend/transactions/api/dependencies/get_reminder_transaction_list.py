from decimal import Decimal
from typing import List, Optional, Dict, Any
from datetime import date, timedelta, datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from administration.api.dependencies.get_todays_date_timezone_adjusted import (
    get_todays_date_timezone_adjusted,
)
from reminders.models import Reminder, ReminderExclusion, Repeat
from transactions.models import TransactionStatus
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


def get_reminder_transaction_list(
    end_date: date, account: int, forecast: Optional[bool] = False
):
    """
    The function `get_reminder_transaction_list` returns a list of
    temporary reminder transactions

    Args:
        start_date (Date): The first date of the transactions.
        end_date (Date): The last date of the transactions.
        account (Int): The ID of the account to get transactions for.

    Returns:
        transactions: List of reminder transaction objects
    """

    # Setup variables
    today = get_todays_date_timezone_adjusted()
    reminder_transactions_list = []
    temp_id = -1

    # Get Reminders for account that have a next date within time frame
    reminders = Reminder.objects.filter(
        Q(reminder_source_account_id=account)
        | Q(reminder_destination_account_id=account),
        next_date__lte=end_date,
    )

    # Get a Pending status object
    status = TransactionStatus.objects.get(id=1)

    # Create temporary transactions based on reminders
    for reminder in reminders:
        new_transaction_date = reminder.next_date
        destination_account = None
        destination_account_name = None
        if reminder.reminder_destination_account:
            destination_account = reminder.reminder_destination_account.id
            destination_account_name = (
                reminder.reminder_destination_account.account_name
            )
        source_account_name = reminder.reminder_source_account.account_name
        pretty_account = source_account_name
        pretty_total = reminder.amount
        if reminder.transaction_type.id == 3:
            pretty_account = (
                source_account_name + " => " + destination_account_name
            )
            if reminder.reminder_source_account.id == account:
                pretty_total = -abs(reminder.amount)
            else:
                pretty_total = abs(reminder.amount)
        if reminder.transaction_type.id == 1:
            pretty_total = -abs(reminder.amount)
        if reminder.transaction_type.id == 2:
            pretty_total = abs(reminder.amount)
        repeat = Repeat.objects.get(id=reminder.repeat.id)
        tags = []
        tag_object = reminder.tag.tag_name
        tags.append(tag_object)
        while True:
            if not ReminderExclusion.objects.filter(
                reminder_id=reminder.id,
                exclude_date=new_transaction_date,
            ).first():
                new_transaction = {
                    "id": temp_id,
                    "transaction_date": new_transaction_date,
                    "total_amount": Decimal(reminder.amount),
                    "status": status,
                    "memo": reminder.memo,
                    "description": reminder.description,
                    "edit_date": today,
                    "add_date": today,
                    "transaction_type": reminder.transaction_type,
                    "paycheck": None,
                    "checkNumber": None,
                    "pretty_total": Decimal(pretty_total),
                    "pretty_account": pretty_account,
                    "source_account_id": reminder.reminder_source_account.id,
                    "destination_account_id": destination_account,
                    "balance": Decimal(0.00),
                    "tags": tags,
                    "reminder_id": reminder.id,
                }
                reminder_transactions_list.append(new_transaction)
                temp_id -= 1
            new_transaction_date += relativedelta(days=repeat.days)
            new_transaction_date += relativedelta(weeks=repeat.weeks)
            new_transaction_date += relativedelta(months=repeat.months)
            new_transaction_date += relativedelta(years=repeat.years)
            if new_transaction_date > end_date or (
                reminder.end_date and new_transaction_date > reminder.end_date
            ):
                break
    return reminder_transactions_list
