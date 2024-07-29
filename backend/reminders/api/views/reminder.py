from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from reminders.models import Reminder
from reminders.api.schemas.reminder import ReminderIn, ReminderOut
from administration.models import logToDB
from django.shortcuts import get_object_or_404
from typing import List
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
from django.db.models.functions import Concat, Coalesce, Abs
from typing import List, Optional, Dict, Any

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
        logToDB(
            f"Reminder created : {reminder.description}",
            None,
            reminder.id,
            None,
            3001001,
            1,
        )
        return {"id": reminder.id}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Reminder not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
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
        reminder.save()
        logToDB(
            f"Reminder updated : #{reminder_id}",
            None,
            reminder_id,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Reminder not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
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
        logToDB(
            f"Reminder retrieved : {reminder.description}",
            None,
            reminder.id,
            None,
            3001006,
            1,
        )
        return reminder
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Reminder not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
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
        logToDB(
            "Reminder list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Reminder list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
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
        logToDB(
            f"Reminder deleted : #{reminder_description}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Reminder not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, f"Record retrieval error: {str(e)}")
