from ninja import Router
from django.db import IntegrityError
from ninja.errors import HttpError
from accounts.models import Bank
from accounts.api.schemas.bank import BankIn, BankOut
from django.shortcuts import get_object_or_404
from typing import List
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

bank_router = Router(tags=["Banks"])


@bank_router.post("/create")
def create_bank(request, payload: BankIn):
    """
    The function `create_bank` creates a bank

    Args:
        request ():
        payload (BankIn): An object using schema of BankIn.

    Returns:
        id: returns the id of the created bank
    """

    try:
        bank = Bank.objects.create(**payload.dict())
        api_logger.info(f"Bank created : {bank.bank_name}")
        return {"id": bank.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Bank not created : bank exists ({payload.bank_name})"
            )
            error_logger.error(
                f"Bank not created : bank exists ({payload.bank_name})"
            )
            raise HttpError(400, "Bank already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Bank not created : db integrity error")
            error_logger.error("Bank not created : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Bank not created")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record creation error")


@bank_router.put("/update/{bank_id}")
def update_bank(request, bank_id: int, payload: BankIn):
    """
    The function `update_bank` updates the bank specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        bank_id (int): the id of the bank to update
        payload (BankIn): a bank object

    Returns:
        success: True

    Raises:
        Http404: If the bank with the specified ID does not exist.
    """

    try:
        bank = get_object_or_404(Bank, id=bank_id)
        bank.bank_name = payload.bank_name
        bank.save()
        api_logger.info(f"Bank updated : {bank.bank_name}")
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Bank not updated : bank exists ({payload.bank_name})"
            )
            error_logger.error(
                f"Bank not updated : bank exists ({payload.bank_name})"
            )
            raise HttpError(400, "Bank already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Bank not updated : db integrity error")
            error_logger.error("Bank not updated : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Bank not updated")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record update error")


@bank_router.get("/get/{bank_id}", response=BankOut)
def get_bank(request, bank_id: int):
    """
    The function `get_bank` retrieves the bank by id

    Args:
        request (HttpRequest): The HTTP request object
        bank_id (int): The id of the bank to retrieve.

    Returns:
        BankOut: the bank object

    Raises:
        Http404: If the bank with the specified ID does not exist.
    """

    try:
        bank = get_object_or_404(Bank, id=bank_id)
        api_logger.debug(f"Bank retrieved : {bank.bank_name}")
        return bank
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Bank not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@bank_router.get("/list", response=List[BankOut])
def list_banks(request):
    """
    The function `list_banks` retrieves a list of banks,
    orderd by bank name ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        BankOut: a list of bank objects
    """

    try:
        qs = Bank.objects.all().order_by("bank_name")
        api_logger.debug("Bank list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Bank list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@bank_router.delete("/delete/{bank_id}")
def delete_bank(request, bank_id: int):
    """
    The function `delete_bank` deletes the bank specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        bank_id (int): the id of the bank to delete

    Returns:
        success: True

    Raises:
        Http404: If the bank with the specified ID does not exist.
    """

    try:
        bank = get_object_or_404(Bank, id=bank_id)
        bank_name = bank.bank_name
        bank.delete()
        api_logger.info(f"Bank deleted : {bank_name}")
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Bank not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
