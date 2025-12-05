from ninja import Router
from ninja.errors import HttpError
from administration.models import Option
from administration.api.schemas.option import OptionIn, OptionOut
from django.shortcuts import get_object_or_404
from typing import List
from administration.api.dependencies.apply_patch import apply_patch
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

option_router = Router(tags=["Options"])


@option_router.patch("/update/{option_id}")
def update_option(request, option_id: int, payload: OptionIn):
    """
    The function `update_option` updates the option specified by id,
    patching the option if a field is sent in the payload.

    Args:
        request (HttpRequest): The HTTP request object.
        option_id (int): the id of the option to update
        payload (OptionIn): an option object

    Returns:
        success: True

    Raises:
        Http404: If the option with the specified ID does not exist.
    """

    try:
        option = get_object_or_404(Option, id=option_id)
        apply_patch(option, payload)

        option.save()
        api_logger.info(f"Option updated : {option_id}")
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Option not updated")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record update error")


@option_router.get("/get/{option_id}", response=OptionOut)
def get_option(request, option_id: int):
    """
    The function `get_option` retrieves the option by id

    Args:
        request (HttpRequest): The HTTP request object.
        option_id (int): The id of the option to retrieve.

    Returns:
        OptionOut: the option object

    Raises:
        Http404: If the option with the specified ID does not exist.
    """

    try:
        option = get_object_or_404(Option, id=option_id)
        api_logger.debug(f"Option retrieved : #{option.id}")
        return option
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Option not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@option_router.get("/list", response=List[OptionOut])
def list_options(request):
    """
    The function `list_options` retrieves a list of options,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        OptionOut: a list of option objects
    """

    try:
        qs = Option.objects.all().order_by("id")
        api_logger.debug("Option list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Option list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@option_router.delete("/delete/{option_id}")
def delete_option(request, option_id: int):
    """
    The function `delete_option` deletes the option specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        option_id (int): the id of the option to delete

    Returns:
        success: True

    Raises:
        Http404: If the option with the specified ID does not exist.
    """

    try:
        option = get_object_or_404(Option, id=option_id)
        option.delete()
        api_logger.info(f"Option deleted : #{option_id}")
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Option not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
