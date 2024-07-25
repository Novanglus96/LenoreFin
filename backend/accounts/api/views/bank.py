from ninja import Router
from django.db import IntegrityError
from ninja.errors import HttpError
from accounts.models import Bank
from accounts.api.schemas.bank import BankIn, BankOut
from administration.models import logToDB
from django.shortcuts import get_object_or_404
from typing import List

bank_router = Router(tags=["Banks"])


@bank_router.post("/accounts/banks")
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
        logToDB(
            f"Bank created : {bank.bank_name}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": bank.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Bank not created : bank exists ({payload.bank_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Bank already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Bank not created : db integrity error",
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
            f"Bank not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@bank_router.put("/accounts/banks/{bank_id}")
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
        logToDB(
            f"Bank updated : {bank.bank_name}",
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
                f"Bank not updated : bank exists ({payload.bank_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Bank already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Bank not updated : db integrity error",
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
            f"Bank not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@bank_router.get("/accounts/banks/{bank_id}", response=BankOut)
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
        logToDB(
            f"Bank retrieved : {bank.bank_name}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return bank
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Bank not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@bank_router.get("/accounts/banks", response=List[BankOut])
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
        logToDB(
            "Bank list retrieved",
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
            f"Bank list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")
