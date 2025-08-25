"""
Module: tasks.py
Description: Contains task definitions to be scheduuled.

Author: John Adams <johnmadams96@gmail.com>
Date: February 15, 2024
"""

from transactions.models import (
    Transaction,
)
from tags.api.dependencies.custom_tag import CustomTag
from transactions.api.dependencies.create_transactions import (
    create_transactions,
)
from transactions.api.dependencies.full_transaction import FullTransaction
from administration.models import Message, Option
from imports.models import (
    FileImport,
    TransactionImport,
    TransactionImportTag,
    TypeMapping,
    StatusMapping,
    TagMapping,
    AccountMapping,
)
from accounts.models import Account
from reminders.models import Reminder, Repeat, ReminderExclusion
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
import csv
from io import StringIO
from django.db.models import (
    Case,
    When,
    Value,
    F,
    Sum,
    Subquery,
    OuterRef,
    ExpressionWrapper,
    DecimalField,
)
from django.db.models.functions import Coalesce, Abs
import pytz
import os
from administration.api.dependencies.log_to_db import logToDB
from administration.api.dependencies.get_todays_date_timezone_adjusted import (
    get_todays_date_timezone_adjusted,
)
from django.core.management import call_command
from planning.models import Budget
import json
from transactions.api.dependencies.get_transactions_by_tag import (
    get_transactions_by_tag,
)


def create_backup(clean=True, keep=0):
    """
    The function `create_backup` creates a database backup and optionally
    keeps only the last x backups, default is 1.

    Args:
    """
    call_command("dbbackup", "--clean", "--compress")
    call_command("mediabackup", "--clean", "--compress")


def create_message(message_text):
    """
    The function `create_message` creates a Message object for
    displaying a message alert in the app inbox.

    Args:
        message_text (str): The text of the message
    """

    Message.objects.create(
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
                        tag_full_toggle=True,
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


def roll_over_budgets():
    """
    The function `roll_over_budgets` calculates roll over amounts for budgets.

    Args:

    Returns:
        string_return (str): the total # of budgets processed
    """
    try:
        today = get_todays_date_timezone_adjusted()
        budgets = (
            Budget.objects.all().filter(active=True).order_by("name", "id")
        )
        roll_over_budgets = budgets.filter(
            roll_over=True, next_start__lte=today
        )
        non_roll_over_budgets = budgets.filter(roll_over=False)
        non_roll_over_budgets.update(roll_over_amt=0)
        num_of_budgets = 0
        for budget in roll_over_budgets:
            transactions = []
            start_date, end_date, periods_passed, next_start = (
                calculate_repeat_window(budget.start_day, budget.repeat)
            )
            transactions = get_transactions_by_tag(
                end_date, False, start_date, json.loads(budget.tag_ids), True
            )
            total = 0
            for transaction in transactions:
                total += transaction.tag_total
            total_budget = budget.amount * periods_passed
            roll_over_amt = total_budget - abs(total)
            budget.roll_over_amt = roll_over_amt
            budget.next_start = next_start
            budget.save()
            num_of_budgets += 1
        return f"Processed {num_of_budgets}"
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Budget roll overs not calculated : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )


def calculate_repeat_window(start_date: datetime, repeat: Repeat) -> tuple:
    """
    Calculate the current repeat window (start and end date) based on the Repeat object.

    Args:
        start_date (datetime or date): The date when the repetition started.
        repeat (Repeat): The Repeat object containing the interval (days, weeks, months, years).

    Returns:
        tuple: A tuple of (window_start, window_end) for the current repeat window.
    """
    # Combine repeat fields into a single period using relativedelta
    total_period = relativedelta(
        days=repeat.days,
        weeks=repeat.weeks,
        months=repeat.months,
        years=repeat.years,
    )

    # Get the current date (you can use your timezone-adjusted function here)
    today = get_todays_date_timezone_adjusted()

    # Calculate how many total periods have passed since the start date
    periods_passed = 0
    current_period_start = start_date

    while current_period_start + total_period <= today:
        current_period_start += total_period
        periods_passed += 1

    window_start = current_period_start
    previous_end = current_period_start + relativedelta(days=-1)
    next_start = window_start + total_period

    return start_date, previous_end, periods_passed, next_start


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
                        tags = []
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
                                for pair in tag_pairs:
                                    tag_name, tag_amount = pair.split(":")
                                    tag_name = tag_name.strip()
                                    tag_amount = float(tag_amount.strip())
                                    tag_id = (
                                        tag_mappings.filter(file_tag=tag_name)
                                        .first()
                                        .tag_id
                                    )
                                    tag_obj = CustomTag(
                                        tag_name=tag_name,
                                        tag_amount=tag_amount,
                                        tag_id=tag_id,
                                        tag_full_toggle=False,
                                    )
                                    tags.append(tag_obj)
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
                            memo=memo,
                            description=description[:254],
                            edit_date=editDate,
                            add_date=addDate,
                            transaction_type_id=typeID,
                            paycheck_id=None,
                            source_account_id=sourceAccountID,
                            destination_account_id=destinationAccountID,
                            tags=tags,
                            checkNumber=None,
                        )
                        transactions_to_create.append(trans)
                    except Exception as f:
                        errors += 1
                        print(f"#{step} - Error adding row to bulk : {f}")

                if create_transactions(transactions_to_create):

                    # Send message to frontend that import was successful
                    Message.objects.create(
                        message_date=get_todays_date_timezone_adjusted(True),
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
                    raise Exception("Unable to create transactions: ")

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


def archive_transactions():
    """
    The function `archive_transactions` archives older transactions based on the
    options set.

    Args:

    Returns:

    """
    try:
        # Load archive options
        options = Option.objects.get(id=1)

        if options.auto_archive:
            # Set variables
            today = get_todays_date_timezone_adjusted(False)
            year_offset = options.archive_length + 1
            past_date = today - relativedelta(years=year_offset)
            cutoff_year = past_date.year
            cutoff_date = date(cutoff_year, 12, 31)
            print(f"Cutoff date: {cutoff_date}")

            # Set matching transactions status to archive
            transactions = Transaction.objects.filter(
                transaction_date__lte=cutoff_date
            )
            transactions.update(status_id=4)

            # For each account, update archive balance with the sum of all
            # archived transactions

            # Subquery to calculate sum of pretty_total grouped by source_account_id
            source_balance_subquery = (
                Transaction.objects.filter(
                    source_account_id=OuterRef("pk"),
                    status_id=4,
                )
                .annotate(
                    pretty_total=Case(
                        When(
                            transaction_type_id=2, then=Abs(F("total_amount"))
                        ),
                        When(
                            transaction_type_id=1, then=-Abs(F("total_amount"))
                        ),
                        When(
                            transaction_type_id=3,
                            then=Case(
                                When(
                                    source_account_id=OuterRef("pk"),
                                    then=-Abs(F("total_amount")),
                                ),
                                default=Abs(F("total_amount")),
                                output_field=DecimalField(
                                    max_digits=12, decimal_places=2
                                ),
                            ),
                        ),
                        default=Value(
                            0,
                            output_field=DecimalField(
                                max_digits=12, decimal_places=2
                            ),
                        ),
                        output_field=DecimalField(
                            max_digits=12, decimal_places=2
                        ),
                    )
                )
                .values("source_account_id")
                .annotate(balance=Sum("pretty_total"))
                .values("balance")[:1]
            )

            # Subquery to calculate sum of pretty_total grouped by destination_account_id
            destination_balance_subquery = (
                Transaction.objects.filter(
                    destination_account_id=OuterRef("pk"),
                    status_id=4,
                )
                .annotate(
                    pretty_total=Case(
                        When(
                            transaction_type_id=2, then=Abs(F("total_amount"))
                        ),
                        When(
                            transaction_type_id=1, then=-Abs(F("total_amount"))
                        ),
                        When(
                            transaction_type_id=3,
                            then=Case(
                                When(
                                    destination_account_id=OuterRef("pk"),
                                    then=Abs(F("total_amount")),
                                ),
                                default=Abs(F("total_amount")),
                                output_field=DecimalField(
                                    max_digits=12, decimal_places=2
                                ),
                            ),
                        ),
                        default=Value(
                            0,
                            output_field=DecimalField(
                                max_digits=12, decimal_places=2
                            ),
                        ),
                        output_field=DecimalField(
                            max_digits=12, decimal_places=2
                        ),
                    )
                )
                .values("destination_account_id")
                .annotate(balance=Sum("pretty_total"))
                .values("balance")[:1]
            )

            # Annotate the Account queryset with the combined balance
            accounts = (
                Account.objects.all()
                .annotate(
                    source_balance=Coalesce(
                        Subquery(
                            source_balance_subquery,
                            output_field=DecimalField(
                                max_digits=12, decimal_places=2
                            ),
                        ),
                        Value(
                            0,
                            output_field=DecimalField(
                                max_digits=12, decimal_places=2
                            ),
                        ),
                    ),
                    destination_balance=Coalesce(
                        Subquery(
                            destination_balance_subquery,
                            output_field=DecimalField(
                                max_digits=12, decimal_places=2
                            ),
                        ),
                        Value(
                            0,
                            output_field=DecimalField(
                                max_digits=12, decimal_places=2
                            ),
                        ),
                    ),
                )
                .annotate(
                    balance=ExpressionWrapper(
                        F("source_balance") + F("destination_balance"),
                        output_field=DecimalField(
                            max_digits=12, decimal_places=2
                        ),
                    )
                )
            )
            for account in accounts:
                account.archive_balance = account.balance
                account.save()
        else:
            print("No auto archive")
        logToDB(
            "Transactions successfully archived.",
            None,
            None,
            None,
            3001002,
            1,
        )
    except Exception as e:
        logToDB(
            f"Transactions not archived: {e}",
            None,
            None,
            None,
            3001902,
            2,
        )
        return f"Error archiving transactions: {e}"


# TODO: Task to look for negative dips
# TODO: Task to look for under threshold
# TODO: Task to update Credit Card specific information
