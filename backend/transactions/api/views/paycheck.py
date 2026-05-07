from ninja import Router
from ninja.errors import HttpError
from transactions.models import Paycheck
from transactions.api.schemas.paycheck import PaycheckIn, PaycheckOut
from django.shortcuts import get_object_or_404
from django.http import Http404
from typing import List
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

paycheck_router = Router(tags=["Paychecks"])


@paycheck_router.post("/create")
def create_paycheck(request, payload: PaycheckIn):
    """
    The function `create_paycheck` creates a paycheck

    Args:
        request ():
        payload (PaycheckIn): An object using schema of PaycheckIn.

    Returns:
        id: returns the id of the created paycheck
    """

    try:
        paycheck = Paycheck.objects.create(**payload.dict())
        api_logger.info(f"Paycheck created : #{paycheck.id}")
        return {"id": paycheck.id}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Paycheck not created")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record creation error")


@paycheck_router.put("/update/{paycheck_id}")
def update_paycheck(request, paycheck_id: int, payload: PaycheckIn):
    """
    The function `update_paycheck` updates the paycheck specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        paycheck_id (int): the id of the paycheck to update
        payload (PaycheckIn): a paycheck object

    Returns:
        success: True

    Raises:
        Http404: If the paycheck with the specified ID does not exist.
    """

    try:
        paycheck = get_object_or_404(Paycheck, id=paycheck_id)
        paycheck.gross = payload.gross
        paycheck.net = payload.net
        paycheck.taxes = payload.taxes
        paycheck.health = payload.health
        paycheck.pension = payload.pension
        paycheck.fsa = payload.fsa
        paycheck.dca = payload.dca
        paycheck.union_dues = payload.union_dues
        paycheck.four_fifty_seven_b = payload.four_fifty_seven_b
        paycheck.payee_id = payload.payee_id
        paycheck.save()
        api_logger.info(f"Paycheck updated : #{paycheck_id}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Paycheck not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Paycheck not updated")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record update error")


@paycheck_router.get("/get/{paycheck_id}", response=PaycheckOut)
def get_paycheck(request, paycheck_id: int):
    """
    The function `get_paycheck` retrieves the paycheck by id

    Args:
        request (HttpRequest): The HTTP request object.
        paycheck_id (int): The id of the paycheck to retrieve.

    Returns:
        PaycheckOut: the payee object

    Raises:
        Http404: If the paycheck with the specified ID does not exist.
    """

    try:
        paycheck = get_object_or_404(Paycheck, id=paycheck_id)
        api_logger.debug(f"Paycheck retrieved : #{paycheck.id}")
        return paycheck
    except Http404:
        raise HttpError(404, "Paycheck not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Paycheck not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@paycheck_router.get("/list", response=List[PaycheckOut])
def list_paychecks(request):
    """
    The function `list_paychecks` retrieves a list of paychecks,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        PaycheckOut: a list of paycheck objects
    """

    try:
        qs = Paycheck.objects.all().order_by("id")
        api_logger.debug("Paycheck list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Paycheck list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@paycheck_router.delete("/delete/{paycheck_id}")
def delete_paycheck(request, paycheck_id: int):
    """
    The function `delete_paycheck` deletes the paycheck specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        paycheck_id (int): the id of the paycheck to delete

    Returns:
        success: True

    Raises:
        Http404: If the paycheck with the specified ID does not exist.
    """

    try:
        paycheck = get_object_or_404(Paycheck, id=paycheck_id)
        paycheck.delete()
        api_logger.info(f"Paycheck deleted : {paycheck_id}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Paycheck not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Paycheck not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
