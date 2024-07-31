"""
Module: tasks.py
Description: Contains task definitions to be scheduuled.

Author: John Adams <johnmadams96@gmail.com>
Date: February 15, 2024
"""

from django_q.tasks import async_task, result, schedule
import arrow
from transactions.models import (
    Transaction,
    TransactionDetail,
    TransactionStatus,
)
from tags.api.dependencies.custom_tag import CustomTag
from transactions.api.dependencies.create_transactions import (
    create_transactions,
)
from transactions.api.dependencies.full_transaction import FullTransaction
from administration.models import Message, Option, LogEntry
from imports.models import (
    FileImport,
    TransactionImport,
    TransactionImportTag,
    TransactionImportError,
    TypeMapping,
    StatusMapping,
    TagMapping,
    AccountMapping,
)
from accounts.models import Account
from reminders.models import Reminder, Repeat, ReminderExclusion
from django_q.models import Schedule
from datetime import date
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone
import csv
from io import StringIO
from django.db import IntegrityError, connection, transaction
from django.db.models import F, Window
from django.db.models.functions import RowNumber
from decimal import Decimal
import pytz
import os
from administration.api.dependencies.log_to_db import logToDB
from administration.api.dependencies.get_todays_date_timezone_adjusted import (
    get_todays_date_timezone_adjusted,
)


def create_message(message_text):
    """
    The function `create_message` creates a Message object for
    displaying a message alert in the app inbox.

    Args:
        message_text (str): The text of the message
    """

    message_obj = Message.objects.create(
        message_date=get_todays_date_timezone_adjusted(True),
        message=message_text,
        unread=True,
    )


def convert_reminder():
    """
    The function `convert_reminder` converts auto_add reminder transactions
    that have a date of today or earlier.  Resets reminder dates to next dates.

    """

    # Define todays date
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    todayDate = today_tz.strftime("%Y-%m-%d")

    # Get reminders that have a next date of today or earlier
    reminders = Reminder.objects.filter(next_date__lte=todayDate)

    # Add transactions and modify next date
    if reminders and len(reminders) > 0:
        for reminder in reminders:
            if reminder.auto_add:
                if not ReminderExclusion.objects.filter(
                    reminder_id=reminder.id, exclude_date=todayDate
                ).first():
                    # If auto_add is True, add transaction
                    transactions_to_create = []
                    tags = []
                    tag_obj = CustomTag(
                        tag_name=reminder.tag.tag_name,
                        tag_amount=reminder.amount,
                        tag_id=reminder.tag.id,
                    )
                    tags.append(tag_obj)
                    destination_account = None
                    if reminder.reminder_destination_account:
                        destination_account = (
                            reminder.reminder_destination_account.id
                        )
                    transaction = FullTransaction(
                        transaction_date=todayDate,
                        total_amount=reminder.amount,
                        status_id=1,
                        memo=reminder.memo,
                        description=reminder.description,
                        edit_date=todayDate,
                        add_date=todayDate,
                        transaction_type_id=reminder.transaction_type.id,
                        paycheck_id=None,
                        source_account_id=reminder.reminder_source_account.id,
                        destination_account_id=destination_account,
                        tags=tags,
                        checkNumber=None,
                    )
                    transactions_to_create.append(transaction)
                    create_transactions(transactions_to_create)
                    logToDB(
                        "Reminder transaction auto-added",
                        None,
                        reminder.id,
                        None,
                        3001002,
                        1,
                    )

            # Modify the next due and start date of the reminder
            repeat = Repeat.objects.get(id=reminder.repeat.id)
            nextDate = today_tz

            # Loop through to find next date not excluded
            while True:
                nextDate += relativedelta(days=repeat.days)
                nextDate += relativedelta(weeks=repeat.weeks)
                nextDate += relativedelta(months=repeat.months)
                nextDate += relativedelta(years=repeat.years)
                if not ReminderExclusion.objects.filter(
                    reminder_id=reminder.id, exclude_date=nextDate
                ).first():
                    break

            # Check if the next date is not after Reminder end date, delete
            # reminder if it is.
            if (
                reminder.end_date is not None and nextDate <= reminder.end_date
            ) or reminder.end_date is None:
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
    success = None
    max_bulk = 1000

    def chunk_list(lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i : i + chunk_size]

    # Check if there are any file imports
    file_imports = FileImport.objects.filter(processed=False)

    # If there is an import, process it
    if file_imports.exists():
        for file, file_import in enumerate(file_imports, start=1):
            file_import.processed = True
            file_import.save()
            transactions_to_create = []
            transaction_details = []
            details_to_create = []
            try:
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
                for step, row in enumerate(rows, start=0):
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
                        editDate = None
                        addDate = None
                        transaction_line = transaction_lines.filter(
                            line_id=step
                        ).first()
                        if transaction_line is not None:
                            transDate = transaction_line.transaction_date
                            totalAmount = float(transaction_line.amount)
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
                            editDate = transDate
                            addDate = transDate
                        else:

                            class CustomTag:
                                def __init__(
                                    self, tag_name, tag_amount, tag_id
                                ):
                                    self.tag_name = tag_name
                                    self.tag_amount = tag_amount
                                    self.tag_id = tag_id

                            transDate = row["TransactionDate"]
                            totalAmount = float(row["Amount"])
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
                            if row["Tags"] and row["Tags"] != 0:
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
                            addDate = transDate
                            editDate = transDate
                        if typeID == 2:
                            totalAmount = abs(float(totalAmount))
                        else:
                            totalAmount = -abs(float(totalAmount))
                        trans = FullTransaction(
                            transaction_date=transDate,
                            total_amount=totalAmount,
                            status_id=statusID,
                            memo=memo[:508],
                            description=description[:254],
                            edit_date=editDate,
                            add_date=addDate,
                            transaction_type_id=typeID,
                            reminder_id=None,
                            paycheck_id=None,
                            source_account_id=sourceAccountID,
                            destination_account_id=destinationAccountID,
                            tags=tags,
                        )
                        transactions_to_create.append(trans)
                    except Exception as f:
                        errors += 1
                        print(f"#{step} - Error adding row to bulk : {f}")

                if create_transactions(transactions_to_create):

                    # Send message to frontend that import was successful
                    message_obj = Message.objects.create(
                        message_date=timezone.now(),
                        message=f"Import # {file_import.id} completed successfully with {errors} errors",
                        unread=True,
                    )

                    # Clean up file import
                    success = True

                    # Log success
                    print(
                        f"Import # {file_import.id} succeeded with {errors} errors"
                    )
                    logToDB(
                        f"Import # {file_import.id} succeeded with {errors} errors",
                        None,
                        None,
                        None,
                        3002001,
                        2,
                    )
                else:
                    raise Exception("Unable to create transactions")

            except Exception as e:
                success = False
                print(f"Import # {file_import.id} failed : {str(e)}")
                logToDB(
                    f"Import # {file_import.id} failed : {str(e)}",
                    None,
                    None,
                    None,
                    3002901,
                    3,
                )
            file_import.successful = success
            file_import.errors = errors
            file_import.save()
            num_of_imports = file
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
    try:
        # setup variables
        today = timezone.now()
        tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
        todayDate = today.astimezone(tz_timezone).date()
        maxDate = todayDate + relativedelta(years=10)
        trans_total = 0
        transactions_to_create = []

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
                tags = []
                tag_obj = CustomTag(
                    tag_name=None,
                    tag_amount=reminder.amount,
                    tag_id=reminder.tag.id,
                )
                tags.append(tag_obj)
                new_transaction = FullTransaction(
                    transaction_date=next_date,
                    total_amount=reminder.amount,
                    status_id=1,
                    description=reminder.description,
                    edit_date=todayDate,
                    add_date=todayDate,
                    transaction_type_id=reminder.transaction_type.id,
                    reminder_id=reminder.id,
                    paycheck_id=None,
                    source_account_id=reminder.reminder_source_account.id,
                    destination_account_id=reminder.reminder_destination_account.id,
                    tags=tags,
                )
                transactions_to_create.append(new_transaction)
                trans_total += 1
                # Increment next_date
                next_date += relativedelta(days=reminder.repeat.days)
                next_date += relativedelta(weeks=reminder.repeat.weeks)
                next_date += relativedelta(months=reminder.repeat.months)
                next_date += relativedelta(years=reminder.repeat.years)
            try:
                create_transactions(transactions_to_create)
                logToDB(
                    "Reminder transactions created",
                    None,
                    reminder.id,
                    None,
                    3002007,
                    1,
                )
            except Exception as e:
                logToDB(
                    f"Reminder transactions error: {e}",
                    None,
                    reminder.id,
                    None,
                    3002907,
                    2,
                )
            string_return = f"Created {trans_total} new transaction(s)"
            return string_return
    except Exception as e:
        logToDB(
            f"Reminder transactions not created: {e}",
            None,
            reminder.id,
            None,
            3002907,
            2,
        )
        return f"Error updating forever reminders: {e}"


# TODO: Task to look for negative dips
# TODO: Task to look for under threshold
# TODO: Task to update Credit Card specific information
