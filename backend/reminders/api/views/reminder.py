from ninja import Router
from ninja.errors import HttpError
from reminders.models import Reminder
from reminders.api.schemas.reminder import (
    ReminderIn,
    ReminderOut,
    ReminderTransIn,
)
from django.shortcuts import get_object_or_404
from django.http import Http404
from typing import List
from reminders.services import add_reminder_transaction, ReminderNotFound
from transactions.tasks import update_reminder_cache
import logging

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

reminder_router = Router(tags=["Reminders"])


@reminder_router.post("/create")
def create_reminder(request, payload: ReminderIn):
    try:
        reminder = Reminder.objects.create(**payload.dict())
        api_logger.info(f"Reminder created : {reminder.description}")
        return {"id": reminder.id}
    except Exception as e:
        api_logger.error("Reminder not created")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record creation error")


@reminder_router.put("/update/{reminder_id}")
def update_reminder(request, reminder_id: int, payload: ReminderIn):
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
        api_logger.error("Reminder not updated")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record update error")


@reminder_router.get("/get/{reminder_id}", response=ReminderOut)
def get_reminder(request, reminder_id: int):
    try:
        reminder = get_object_or_404(Reminder, id=reminder_id)
        api_logger.debug(f"Reminder retrieved : {reminder.description}")
        return reminder
    except Http404:
        raise HttpError(404, "Reminder not found")
    except Exception as e:
        api_logger.error("Reminder not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@reminder_router.get("/list", response=List[ReminderOut])
def list_reminders(request):
    try:
        qs = Reminder.objects.all().order_by("next_date", "id")
        api_logger.debug("Reminder list retrieved")
        return qs
    except Exception as e:
        api_logger.error("Reminder list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@reminder_router.delete("/delete/{reminder_id}")
def delete_reminder(request, reminder_id: int):
    try:
        reminder = get_object_or_404(Reminder, id=reminder_id)
        reminder_description = reminder.description
        reminder.delete()
        api_logger.info(f"Reminder deleted : #{reminder_description}")
        return {"success": True}
    except Exception as e:
        api_logger.error("Reminder not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@reminder_router.put("/addtrans/{reminder_id}")
def add_reminder_trans(request, reminder_id: int, payload: ReminderTransIn):
    try:
        add_reminder_transaction(reminder_id, payload.transaction_date)
        update_reminder_cache(reminder_id)
        api_logger.info(f"Reminder transaction added : #{reminder_id}")
        return {"success": True}
    except ReminderNotFound:
        raise HttpError(404, "Reminder not found")
    except Exception as e:
        api_logger.error("Reminder transaction not added")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record update error : {str(e)}")
