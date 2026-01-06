from ninja import Router
from ninja.errors import HttpError
from reminders.models import Reminder, ReminderExclusion, Repeat
from transactions.models import Transaction
from reminders.api.schemas.reminder import (
    ReminderIn,
    ReminderOut,
    ReminderTransIn,
)
from django.shortcuts import get_object_or_404
from typing import List
from dateutil.relativedelta import relativedelta
from tags.api.dependencies.custom_tag import CustomTag
from transactions.api.dependencies.full_transaction import FullTransaction
from transactions.api.dependencies.create_transactions import (
    create_transactions,
)
from utils.dates import (
    get_todays_date_timezone_adjusted,
)
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

reminder_router = Router(tags=["Reminders"])


@reminder_router.post("/create")
def create_reminder(request, payload: ReminderIn):
    """
    The function `create_reminder` creates a reminder

    Args:
        request ():
        payload (ReminderIn): An object using schema of ReminderIn.

    Returns:
        id: returns the id of the created reminder
    """

    try:
        reminder = Reminder.objects.create(**payload.dict())
        api_logger.info(f"Reminder created : {reminder.description}")
        return {"id": reminder.id}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Reminder not created")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record creation error")


@reminder_router.put("/update/{reminder_id}")
def update_reminder(request, reminder_id: int, payload: ReminderIn):
    """
    The function `update_reminder` updates the reminder specified by id.
    Related transactions are deleted and recreated.

    Args:
        request (HttpRequest): The HTTP request object.
        reminder_id (int): the id of the reminder to update
        payload (ReminderIn): a reminder object

    Returns:
        success: True

    Raises:
        Http404: If the reminder with the specified ID does not exist.
    """

    try:
        reminder = get_object_or_404(Reminder, id=reminder_id)
        reminder.tag_id = payload.tag_id
        reminder.amount = payload.amount
        reminder.reminder_source_account_id = payload.reminder_source_account_id
        reminder.reminder_destination_account_id = (
            payload.reminder_destination_account_id
        )
        reminder.description = payload.description
        reminder.transaction_type_id = payload.transaction_type_id
        reminder.start_date = payload.start_date
        reminder.next_date = payload.next_date
        reminder.end_date = payload.end_date
        reminder.repeat_id = payload.repeat_id
        reminder.auto_add = payload.auto_add
        reminder.memo = payload.memo
        reminder.save()
        api_logger.info(f"Reminder updated : #{reminder_id}")
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Reminder not updated")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record update error")


@reminder_router.get("/get/{reminder_id}", response=ReminderOut)
def get_reminder(request, reminder_id: int):
    """
    The function `get_reminder` retrieves the reminder by id

    Args:
        request (HttpRequest): The HTTP request object.
        reminder_id (int): The id of the reminder to retrieve.

    Returns:
        ReminderOut: the reminder object

    Raises:
        Http404: If the reminder with the specified ID does not exist.
    """

    try:
        reminder = get_object_or_404(Reminder, id=reminder_id)
        api_logger.debug(f"Reminder retrieved : {reminder.description}")
        return reminder
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Reminder not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@reminder_router.get("/list", response=List[ReminderOut])
def list_reminders(request):
    """
    The function `list_reminders` retrieves a list of reminders,
    ordered by next date ascending and then id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        ReminderOut: a list of reminders objects
    """

    try:
        qs = Reminder.objects.all().order_by("next_date", "id")
        api_logger.debug("Reminder list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Reminder list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@reminder_router.delete("/delete/{reminder_id}")
def delete_reminder(request, reminder_id: int):
    """
    The function `delete_reminder` deletes the reminder specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        reminder_id (int): the id of the reminder to delete

    Returns:
        success: True

    Raises:
        Http404: If the reminder with the specified ID does not exist.
    """

    try:
        reminder = get_object_or_404(Reminder, id=reminder_id)
        reminder_description = reminder.description
        reminder.delete()
        api_logger.info(f"Reminder deleted : #{reminder_description}")
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Reminder not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@reminder_router.put("/addtrans/{reminder_id}")
def add_reminder_trans(request, reminder_id: int, payload: ReminderTransIn):
    """
    The function `add_reminder_trans` converts a reminder temp transaction into
    a transaction and exludes the date from the reminder series.

    Args:
        request (HttpRequest): The HTTP request object.
        reminder_id (int): the id of the reminder to update
        payload (ReminderTransIn): a ReminderTransIn object

    Returns:
        success: True

    Raises:
        Http404: If the reminder with the specified ID does not exist.
    """

    try:
        # Load the reminder information
        reminder = Reminder.objects.get(id=reminder_id)

        # Verify the transaction doesn't exist
        existing_transaction = Transaction.objects.filter(
            transaction_date=payload.transaction_date,
            total_amount=reminder.amount,
            memo=reminder.memo,
            description=reminder.description,
            transaction_type=reminder.transaction_type,
            destination_account=reminder.reminder_destination_account,
            source_account=reminder.reminder_source_account,
        ).last()
        if not existing_transaction:
            transactions_to_create = []
            tags = []
            destination_account = None
            if reminder.reminder_destination_account:
                destination_account = reminder.reminder_destination_account.id
            # Create tags list
            tag_obj = CustomTag(
                tag_name=None,
                tag_amount=reminder.amount,
                tag_id=reminder.tag.id,
                tag_full_toggle=True,
            )
            tags.append(tag_obj)

            # Add transaction
            transaction = FullTransaction(
                transaction_date=payload.transaction_date,
                total_amount=reminder.amount,
                status_id=1,
                memo=reminder.memo,
                description=reminder.description,
                edit_date=get_todays_date_timezone_adjusted(),
                add_date=get_todays_date_timezone_adjusted(),
                transaction_type_id=reminder.transaction_type.id,
                paycheck_id=None,
                source_account_id=reminder.reminder_source_account.id,
                destination_account_id=destination_account,
                tags=tags,
                checkNumber=None,
            )
            transactions_to_create.append(transaction)
            if create_transactions(transactions_to_create):
                api_logger.info("Transaction created")

        # Verify the exclusion doesn't exist
        existing_exclusion = ReminderExclusion.objects.filter(
            reminder=reminder, exclude_date=payload.transaction_date
        ).last()

        # Add exclusion
        if not existing_exclusion:
            exclusion = ReminderExclusion.objects.create(
                reminder=reminder,
                exclude_date=payload.transaction_date,
            )

        # Change next date to next not excluded date
        nextDate = reminder.next_date
        repeat = Repeat.objects.get(id=reminder.repeat.id)
        while True:
            if not ReminderExclusion.objects.filter(
                reminder_id=reminder.id, exclude_date=nextDate
            ).first():
                break
            nextDate += relativedelta(days=repeat.days)
            nextDate += relativedelta(weeks=repeat.weeks)
            nextDate += relativedelta(months=repeat.months)
            nextDate += relativedelta(years=repeat.years)
        reminder.next_date = nextDate
        reminder.save()

        api_logger.info(f"Reminder transaction added : #{reminder_id}")
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Reminder transaction not added")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record update error : {str(e)}")
