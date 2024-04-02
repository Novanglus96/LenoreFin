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
    FileImport,
    TransactionImport,
    TransactionImportTag,
    TransactionImportError,
    TypeMapping,
    StatusMapping,
    TagMapping,
    AccountMapping,
)
from django_q.models import Schedule
from datetime import date
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone
import csv
from io import StringIO


def create_message(message_text):
    """
    The function `create_message` creates a Message object for
    displaying a message alert in the app inbox.

    Args:
        message_text (str): The text of the message
    """

    message_obj = Message.objects.create(
        message_date=timezone.now(),
        message=message_text,
        unread=True,
    )


def convert_reminder():
    """
    The function `convert_reminder` converts auto_add reminder transactions
    that have a date of today or earlier.  Resets reminder dates to next dates.

    """

    # Define todays date
    todayDate = timezone.now().date().strftime("%Y-%m-%d")

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


def finish_imports():
    """
    The function `finish_imports` imports files using the mappings defined.

    Args:

    Returns:
        string_return (str): the total # of imports processed
    """
    # Setup variables
    string_return = ""
    num_of_imports = 0
    rows = None
    errors = 0

    # Check if there are any file imports
    file_imports = FileImport.objects.all()

    # If there is an import, process it
    if file_imports.exists():
        try:
            num_of_imports = file_imports.count()
            for file_import in file_imports:
                # Load and parse import file
                file_content = file_import.import_file.read().decode(
                    "utf-8-sig"
                )
                file_like_object = StringIO(file_content)
                reader = csv.DictReader(file_like_object)
                rows = list(reader)

                # Load mappings
                transaction_types = TypeMapping.objects.filter(
                    file_import=file_import
                )
                transaction_statuses = StatusMapping.objects.filter(
                    file_import=file_import
                )
                tag_mappings = TagMapping.objects.filter(
                    file_import=file_import
                )
                account_mappings = AccountMapping.objects.filter(
                    file_import=file_import
                )
                transaction_lines = TransactionImport.objects.filter(
                    file_import=file_import
                )

                # Create transactions based on mappings
                line_num = 0
                for row in rows:
                    try:
                        transDate = None
                        totalAmount = None
                        statusID = None
                        memo = None
                        description = None
                        typeID = None
                        tags = None
                        sourceAccountID = None
                        destinationAccountID = None
                        editDate = timezone.now().date().strftime("%Y-%m-%d")
                        addDate = timezone.now().date().strftime("%Y-%m-%d")
                        transaction_line = transaction_lines.filter(
                            line_id=line_num
                        ).first()
                        if transaction_line is not None:
                            transDate = transaction_line.transaction_date
                            totalAmount = transaction_line.amount
                            statusID = transaction_line.transaction_status_id
                            memo = transaction_line.memo
                            description = transaction_line.description
                            typeID = transaction_line.transaction_type_id
                            tags = TransactionImportTag.objects.filter(
                                transaction_import=transaction_line
                            )
                            destinationAccountID = (
                                transaction_line.destination_account_id
                            )
                            sourceAccountID = transaction_line.source_account_id
                        else:

                            class CustomTag:
                                def __init__(
                                    self, tag_name, tag_amount, tag_id
                                ):
                                    self.tag_name = tag_name
                                    self.tag_amount = tag_amount
                                    self.tag_id = tag_id

                            transDate = row["TransactionDate"]
                            totalAmount = row["Amount"]
                            statusID = (
                                transaction_statuses.filter(
                                    file_status=row["TransactionStatus"]
                                )
                                .first()
                                .status_id
                            )
                            memo = row["Memo"]
                            description = row["Description"]
                            typeID = (
                                transaction_types.filter(
                                    file_type=row["TransactionType"]
                                )
                                .first()
                                .type_id
                            )
                            sourceAccountID = (
                                account_mappings.filter(
                                    file_account=row["SourceAccount"]
                                )
                                .first()
                                .account_id
                            )
                            destinationAccount = account_mappings.filter(
                                file_account=row["DestinationAccount"]
                            ).first()
                            if destinationAccount is not None:
                                destinationAccountID = (
                                    destinationAccount.account_id
                                )
                            tag_pairs = row["Tags"].split(";")
                            tags = []
                            for pair in tag_pairs:
                                tag_name, tag_amount = pair.split(":")
                                tag_name = tag_name.strip()
                                tag_amount = float(tag_amount.strip())
                                tag_id = (
                                    tag_mappings.filter(file_tag=tag_name)
                                    .first()
                                    .tag_id
                                )
                                tag_dict = CustomTag(
                                    tag_name, tag_amount, tag_id
                                )
                                tags.append(tag_dict)
                        transaction = Transaction.objects.create(
                            transaction_date=transDate,
                            total_amount=totalAmount,
                            status_id=statusID,
                            memo=memo,
                            description=description,
                            edit_date=editDate,
                            add_date=addDate,
                            transaction_type_id=typeID,
                            reminder_id=None,
                            paycheck_id=None,
                        )
                        if typeID == 3:
                            TransactionDetail.objects.create(
                                transaction_id=transaction.id,
                                account_id=sourceAccountID,
                                detail_amt=totalAmount,
                                tag_id=2,
                            )
                            TransactionDetail.objects.create(
                                transaction_id=transaction.id,
                                account_id=destinationAccountID,
                                detail_amt=-totalAmount,
                                tag_id=2,
                            )
                        else:
                            for tag in tags:
                                adj_amount = 0
                                if typeID == 1:
                                    adj_amount = -tag.tag_amount
                                else:
                                    adj_amount = tag.tag_amount
                                TransactionDetail.objects.create(
                                    transaction_id=transaction.id,
                                    account_id=sourceAccountID,
                                    detail_amt=adj_amount,
                                    tag_id=tag.tag_id,
                                )
                        line_num += 1
                        logToDB(
                            "Import transaction created",
                            None,
                            None,
                            None,
                            3001001,
                            2,
                        )
                    except Exception as e:
                        error += 1
                        logToDB(
                            f"Import transaction not created : {str(e)}",
                            None,
                            None,
                            None,
                            3001901,
                            3,
                        )
                # Send message to frontend that import was successful
                message_obj = Message.objects.create(
                    message_date=timezone.now(),
                    message=f"Import # {file_import.id} completed successfully with {errors} errors",
                    unread=True,
                )

                # Clean up file import
                file_import.delete()

                # Log success
                logToDB(
                    f"Import # {file_import.id} succeeded",
                    None,
                    None,
                    None,
                    3002001,
                    2,
                )
        except Exception as e:
            logToDB(
                f"Import # {file_import.id} failed : {str(e)}",
                None,
                None,
                None,
                3002901,
                3,
            )
    string_return = f"Processed {num_of_imports} imports with {errors} errors"
    return string_return


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
