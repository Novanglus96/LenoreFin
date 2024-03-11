"""
Module: tasks.py
Description: Contains task definitions to be scheduuled.

Author: John Adams <johnmadams96@gmail.com>
Date: February 15, 2024
"""

from django_q.tasks import async_task, result, schedule
import arrow
from api.models import (
    Message,
    Reminder,
    Transaction,
    Repeat,
    Option,
    LogEntry,
    TransactionDetail,
)
from django_q.models import Schedule
from datetime import date
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone


def create_message(message_text):
    """
    The function `create_message` creates a Message object for
    displaying a message alert in the app inbox.

    Args:
        message_text (str): The text of the message
    """

    message_obj = Message.objects.create(
        message_date=date.today().strftime("%Y-%m-%d"),
        message=message_text,
        unread=True,
    )


def convert_reminder():
    """
    The function `convert_reminder` converts auto_add reminder transactions
    that have a date of today or earlier.  Resets reminder dates to next dates.

    """

    # Define todays date
    todayDate = timzezone.now().date().strftime("%Y-%m-%d")

    # Get transactions that have a reminder and are dated today or earlier
    transactions = Transaction.objects.filter(
        transaction_date__lte=todayDate, reminder__isnull=False
    )

    # Check for auto_add
    if transactions.exists():
        for transaction in transactions:
            reminder = transaction.reminder
            repeat = reminder.repeat
            if reminder.auto_add:
                # If auto_add is True, delete the reminder association
                transaction.reminder = None
                transaction.save()
                logToDB(
                    "Reminder transaction auto-added",
                    None,
                    reminder.id,
                    transaction.id,
                    3001002,
                    1,
                )
            else:
                # If auto_add is False, delete the transaction
                transaction.delete()
                logToDB(
                    "Reminder transaction deleted",
                    None,
                    reminder.id,
                    None,
                    3001003,
                    1,
                )

            # Modify the next due and start date of the reminder
            nextDate = timezone.now().date()
            nextDate += relativedelta(days=repeat.days)
            nextDate += relativedelta(weeks=repeat.weeks)
            nextDate += relativedelta(months=repeat.months)
            nextDate += relativedelta(years=repeat.years)

            # Check if the next date is not after Reminder end date, delete
            # reminder if it is.
            if nextDate <= reminder.end_date:
                reminder.next_date = nextDate
                reminder.start_date = nextDate
                reminder.save()
                logToDB(
                    "Reminder dates reset",
                    None,
                    reminder.id,
                    None,
                    3001002,
                    1,
                )
            else:
                reminder.delete()
                logToDB(
                    "Reminder deleted: no more transactions",
                    None,
                    None,
                    None,
                    3001003,
                    1,
                )


# TODO: Task to update forever reminders


def update_forever_reminders():
    """
    The function `update_forever_reminders` updates reminders that have no end date to always have
    data for 10 years.

    Args:

    Returns:
        trans_total (int): the total number of transactions created

    """
    # setup variables
    todayDate = timezone.now().date()
    maxDate = todayDate + relativedelta(years=10)
    trans_total = 0

    # Retrieve reminders with no end date
    reminders = Reminder.objects.filter(end_date__isnull=True)
    for reminder in reminders:
        # Get last transaction
        last_transaction = (
            Transaction.objects.filter(reminder_id=reminder.id)
            .order_by("-transaction_date")
            .first()
        )
        last_date = last_transaction.transaction_date
        next_date = last_date
        next_date += relativedelta(days=reminder.repeat.days)
        next_date += relativedelta(weeks=reminder.repeat.weeks)
        next_date += relativedelta(months=reminder.repeat.months)
        next_date += relativedelta(years=reminder.repeat.years)
        # Add transactions up to 10 years
        while next_date <= maxDate:
            # Add Transaction
            new_transaction = Transaction.objects.create(
                transaction_date=next_date,
                total_amount=reminder.amount,
                status_id=1,
                description=reminder.description,
                edit_date=todayDate,
                add_date=todayDate,
                transaction_type_id=reminder.transaction_type.id,
                reminder_id=reminder.id,
            )
            # Add Detail
            if reminder.transaction_type.id == 3:
                TransactionDetail.objects.create(
                    transaction_id=new_transaction.id,
                    account_id=reminder.reminder_source_account.id,
                    detail_amt=reminder.amount,
                    tag_id=reminder.tag.id,
                )
                TransactionDetail.objects.create(
                    transaction_id=new_transaction.id,
                    account_id=reminder.reminder_destination_account.id,
                    detail_amt=-reminder.amount,
                    tag_id=reminder.tag.id,
                )
            else:
                TransactionDetail.objects.create(
                    transaction_id=new_transaction.id,
                    account_id=reminder.reminder_source_account.id,
                    detail_amt=reminder.amount,
                    tag_id=reminder.tag.id,
                )
            logToDB(
                "Reminder transactions created",
                None,
                reminder.id,
                None,
                3002007,
                1,
            )
            trans_total += 1
            # Increment next_date
            next_date += relativedelta(days=reminder.repeat.days)
            next_date += relativedelta(weeks=reminder.repeat.weeks)
            next_date += relativedelta(months=reminder.repeat.months)
            next_date += relativedelta(years=reminder.repeat.years)
        string_return = f"Created {trans_total} new transaction(s)"
        return string_return


# TODO: Task to look for negative dips
# TODO: Task to look for under threshold
# TODO: Task to update Credit Card specific information
def logToDB(message, account, reminder, transaction, error, level):
    """
    The function `logToDB` creates log entries, but only if the current logging level
    set in options is lower than the specified error level.

    Args:
        message (str): The log entry message.
        account (Account): Optional, the account associated with this entry.
        reminder (Reminder): Optional, the reminder associated with this entry.
        transaction (Transaction): Optional, the transactions associated with this entry.
        error (int): Optional, any error number associated with this entry.
        level (ErrorLevel): The error level of this entry.

    Returns:
        success (int): Returns the id of the created log entry.
    """

    options = get_object_or_404(Option, id=1)
    if options.log_level.id <= level:
        log_entry = LogEntry.objects.create(
            log_entry=message,
            account_id=account,
            reminder_id=reminder,
            transaction_id=transaction,
            error_num=error,
            error_level_id=level,
        )
        return_id = log_entry.id
    else:
        return_id = 0
    return {"success": return_id}
