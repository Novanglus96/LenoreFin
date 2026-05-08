from ninja import Router
from django.db import IntegrityError
from ninja.errors import HttpError
from administration.models import Payee
from administration.api.schemas.payee import PayeeIn, PayeeOut
from django.shortcuts import get_object_or_404
from django.http import Http404
from typing import List
import logging
from administration.api.dependencies.auth import FullAccessAuth

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

payee_router = Router(tags=["Payees"])


@payee_router.post("/create", auth=FullAccessAuth())
def create_payee(request, payload: PayeeIn):
    """
    The function `create_payee` creates a payee

    Args:
        request ():
        payload (PayeeIn): An object using schema of PayeeIn.

    Returns:
        id: returns the id of the created payee
    """

    try:
        payee = Payee.objects.create(**payload.dict())
        api_logger.info(f"Payee created : {payee.payee_name}")
        return {"id": payee.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Payee not created : payee exists ({payload.payee_name})"
            )
            error_logger.error(
                f"Payee not created : payee exists ({payload.payee_name})"
            )
            raise HttpError(400, "Payee already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Payee not created : db integrity error")
            error_logger.error("Payee not created : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Payee not created")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record creation error")


@payee_router.put("/update/{payee_id}", auth=FullAccessAuth())
def update_payee(request, payee_id: int, payload: PayeeIn):
    """
    The function `update_payee` updates the payee specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        payee_id (int): the id of the payee to update
        payload (PayeeIn): a note object

    Returns:
        success: True

    Raises:
        Http404: If the payee with the specified ID does not exist.
    """

    try:
        payee = get_object_or_404(Payee, id=payee_id)
        payee.payee_name = payload.payee_name
        payee.save()
        api_logger.info(f"Payee updated : {payee.payee_name}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Payee not found")
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Payee not updated : payee exists ({payload.payee_name})"
            )
            error_logger.error(
                f"Payee not updated : payee exists ({payload.payee_name})"
            )
            raise HttpError(400, "Payee already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Payee not updated : db integrity error")
            error_logger.error("Payee not updated : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Payee not updated")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record update error")


@payee_router.get("/get/{payee_id}", response=PayeeOut)
def get_payee(request, payee_id: int):
    """
    The function `get_payee` retrieves the payee by id

    Args:
        request (HttpRequest): The HTTP request object.
        payee_id (int): The id of the payee to retrieve.

    Returns:
        PayeeOut: the payee object

    Raises:
        Http404: If the payee with the specified ID does not exist.
    """

    try:
        payee = get_object_or_404(Payee, id=payee_id)
        api_logger.debug(f"Payee retrieved : {payee.payee_name}")
        return payee
    except Http404:
        raise HttpError(404, "Payee not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Payee not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@payee_router.get("/list", response=List[PayeeOut])
def list_payees(request):
    """
    The function `list_payees` retrieves a list of payees,
    ordered by payee name ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        PayeeOut: a list of payee objects
    """

    try:
        qs = Payee.objects.all().order_by("payee_name")
        api_logger.debug("Payee list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Payee list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@payee_router.delete("/delete/{payee_id}", auth=FullAccessAuth())
def delete_payee(request, payee_id: int):
    """
    The function `delete_payee` deletes the payee specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        payee_id (int): the id of the payee to delete

    Returns:
        success: True

    Raises:
        Http404: If the payee with the specified ID does not exist.
    """

    try:
        payee = get_object_or_404(Payee, id=payee_id)
        payee_name = payee.payee_name
        payee.delete()
        api_logger.info(f"Payee deleted : {payee_name}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Payee not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Payee not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
