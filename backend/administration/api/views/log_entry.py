from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from administration.models import LogEntry, Option
from administration.api.schemas.log_entry import LogEntryIn, LogEntryOut
from administration.api.dependencies.log_to_db import logToDB
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

log_entry_router = Router(tags=["Log Entries"])


@log_entry_router.post("/create")
def create_log_entry(request, payload: LogEntryIn):
    """
    The function `create_log_entry` creates a log entry, but only if the log_level_id
    is greater than the current log_level in options

    Args:
        request ():
        payload (LogEntryIn): An object using schema of LogEntryIn.

    Returns:
        id: returns and id of 0
    """

    options = get_object_or_404(Option, id=1)
    if payload.error_level_id >= options.log_level.id:
        log_entry = LogEntry.objects.create(**payload.dict())
        return {"id": log_entry.id}
    return {"id": 0}


@log_entry_router.put("/update/{logentry_id}")
def update_log_entry(request, logentry_id: int, payload: LogEntryIn):
    """
    The function `update_log_entry` updates the log entry specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        logentry_id (int): the id of the log entry to update
        payload (LogEntryIn): a log entry object

    Returns:
        success: True

    Raises:
        Http404: If the log entry with the specified ID does not exist.
    """

    try:
        log_entry = get_object_or_404(LogEntry, id=logentry_id)
        log_entry.log_date = payload.log_date
        log_entry.log_entry = payload.log_entry
        log_entry.account_id = payload.account_id
        log_entry.reminder_id = payload.reminder_id
        log_entry.transaction_id = payload.transaction_id
        log_entry.error_num = payload.error_num
        log_entry.error_level_id = payload.error_level_id
        log_entry.save()
        logToDB(
            f"Log entry updated : #{logentry_id}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Log entry not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@log_entry_router.get("/get/{logentry_id}", response=LogEntryOut)
def get_log_entry(request, logentry_id: int):
    """
    The function `get_log_entry` retrieves the log entry by id

    Args:
        request (HttpRequest): The HTTP request object.
        logentry_id (int): The id of the log entry to retrieve.

    Returns:
        LogEntryOut: the log entry object

    Raises:
        Http404: If the log entry with the specified ID does not exist.
    """

    try:
        log_entry = get_object_or_404(LogEntry, id=logentry_id)
        logToDB(
            f"Log entry retrieved : #{log_entry.id}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return log_entry
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Log entry not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@log_entry_router.get("/list", response=List[LogEntryOut])
def list_log_entries(request, log_level: Optional[int] = Query(0)):
    """
    The function `list_log_entries` retrieves a list of log entries,
    ordered by id ascending and filtered by log level id.

    Args:
        request (HttpRequest): The HTTP request object.
        log_level (int): Optional log level to filter by, default is 0.

    Returns:
        LogEntryOut: a list of log entry objects
    """

    try:
        qs = LogEntry.objects.filter(error_level__id__gte=log_level).order_by(
            "-id"
        )
        logToDB(
            "Log entry list retrieved",
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
            f"Log entry list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@log_entry_router.delete("/delete/{logentry_id}")
def delete_log_entry(request, logentry_id: int):
    """
    The function `delete_log_entry` deletes the log entry specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        logentry_id (int): the id of the log entry to delete

    Returns:
        success: True

    Raises:
        Http404: If the log entry with the specified ID does not exist.
    """

    try:
        log_entry = get_object_or_404(LogEntry, id=logentry_id)
        log_entry.delete()
        logToDB(
            f"Log entry deleted : #{logentry_id}",
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
            f"Log entry not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")
