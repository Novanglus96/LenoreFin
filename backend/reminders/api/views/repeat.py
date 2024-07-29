from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from reminders.models import Repeat
from reminders.api.schemas.repeat import RepeatIn, RepeatOut
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

repeat_router = Router(tags=["Repeats"])


@repeat_router.post("/create")
def create_repeat(request, payload: RepeatIn):
    """
    The function `create_repeat` creates a repeat

    Args:
        request ():
        payload (RepeatIn): An object using schema of RepeatIn.

    Returns:
        id: returns the id of the created repeat
    """

    try:
        repeat = Repeat.objects.create(**payload.dict())
        logToDB(
            f"Repeat created : {repeat.repeat_name}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": repeat.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Repeat not created : repeat exists ({payload.repeat_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Repeat already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Repeat not created : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Repeat not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@repeat_router.put("/update/{repeat_id}")
def update_repeat(request, repeat_id: int, payload: RepeatIn):
    """
    The function `update_repeat` updates the repeat specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        repeat_id (int): the id of repeat to update
        payload (RepeatIn): a repeat object

    Returns:
        success: True

    Raises:
        Http404: If the repeat with the specified ID does not exist.
    """

    try:
        repeat = get_object_or_404(Repeat, id=repeat_id)
        repeat.repeat_name = payload.repeat_name
        repeat.days = payload.days
        repeat.weeks = payload.weeks
        repeat.months = payload.months
        repeat.years = payload.years
        repeat.save()
        logToDB(
            f"Repeat updated : {repeat.repeat_name}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Repeat not updated : repeat exists ({payload.repeat_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Repeat already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Repeat not updated : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Repeat not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@repeat_router.get("/get/{repeat_id}", response=RepeatOut)
def get_repeat(request, repeat_id: int):
    """
    The function `get_repeat` retrieves the repeat by id

    Args:
        request (HttpRequest): The HTTP request object.
        repeat_id (int): The id of the repeat to retrieve.

    Returns:
        RepeatOut: the repeat object

    Raises:
        Http404: If the repeat with the specified ID does not exist.
    """

    try:
        repeat = get_object_or_404(Repeat, id=repeat_id)
        logToDB(
            f"Repeat retrieved : {repeat.repeat_name}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return repeat
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Repeat not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@repeat_router.get("/list", response=List[RepeatOut])
def list_repeats(request):
    """
    The function `list_repeats` retrieves a list of repeats,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        RepeatOut: a list of repeat objects
    """

    try:
        qs = Repeat.objects.all().order_by("id")
        logToDB(
            "Repeat list not retrieved",
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
            f"Repeat list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@repeat_router.delete("/delete/{repeat_id}")
def delete_repeat(request, repeat_id: int):
    """
    The function `delete_repeat` deletes the repeat specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        repeat_id (int): the id of the repeat to delete

    Returns:
        success: True

    Raises:
        Http404: If the repeat with the specified ID does not exist.
    """

    try:
        repeat = get_object_or_404(Repeat, id=repeat_id)
        repeat_name = repeat.repeat_name
        repeat.delete()
        logToDB(
            f"Repeat deleted : {repeat_name}",
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
            f"Repeat not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")
