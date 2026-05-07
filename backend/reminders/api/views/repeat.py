from ninja import Router
from django.db import IntegrityError
from ninja.errors import HttpError
from reminders.models import Repeat
from reminders.api.schemas.repeat import RepeatIn, RepeatOut
from django.shortcuts import get_object_or_404
from typing import List
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

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
        api_logger.info(f"Repeat created : {repeat.repeat_name}")
        return {"id": repeat.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Repeat not created : repeat exists ({payload.repeat_name})"
            )
            error_logger.error(
                f"Repeat not created : repeat exists ({payload.repeat_name})"
            )
            raise HttpError(400, "Repeat already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Repeat not created : db integrity error")
            error_logger.error("Repeat not created : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Repeat not created")
        error_logger.error(f"{str(e)}")
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
        api_logger.info(f"Repeat updated : {repeat.repeat_name}")
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Repeat not updated : repeat exists ({payload.repeat_name})"
            )
            error_logger.error(
                f"Repeat not updated : repeat exists ({payload.repeat_name})"
            )
            raise HttpError(400, "Repeat already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Repeat not updated : db integrity error")
            error_logger.error("Repeat not updated : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Repeat not updated")
        error_logger.error(f"{str(e)}")
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
        api_logger.debug(f"Repeat retrieved : {repeat.repeat_name}")
        return repeat
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Repeat not retrieved")
        error_logger.error(f"{str(e)}")
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
        api_logger.debug("Repeat list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Repeat list not retrieved")
        error_logger.error(f"{str(e)}")
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
        api_logger.info(f"Repeat deleted : {repeat_name}")
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Repeat not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
