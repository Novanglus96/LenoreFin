from ninja import Router
from django.db import IntegrityError
from ninja.errors import HttpError
from transactions.models import TransactionType
from transactions.api.schemas.transaction_type import (
    TransactionTypeIn,
    TransactionTypeOut,
)
from django.shortcuts import get_object_or_404
from django.http import Http404
from typing import List
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

transaction_type_router = Router(tags=["Transaction Types"])


@transaction_type_router.put("/update/{transaction_type_id}")
def update_transaction_type(
    request, transaction_type_id: int, payload: TransactionTypeIn
):
    """
    The function `update_transaction_type` updates the transaction type specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        transactiontype_id (int): the id of the transaction type to update
        payload (TransactionTypeIn): a transaction type object

    Returns:
        success: True

    Raises:
        Http404: If the transaction type with the specified ID does not exist.
    """

    try:
        transaction_type = get_object_or_404(
            TransactionType, id=transaction_type_id
        )
        transaction_type.transaction_type = payload.transaction_type
        transaction_type.save()
        api_logger.info(
            f"Transaction type updated : {transaction_type.transaction_type}"
        )
        return {"success": True}
    except Http404:
        raise HttpError(404, "Transaction type not found")
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Transaction type not updated : transaction type exists ({payload.transaction_type})"
            )
            error_logger.error(
                f"Transaction type not updated : transaction type exists ({payload.transaction_type})"
            )
            raise HttpError(400, "Transaction type already exists")
        else:
            # Log other types of integry errors
            api_logger.error(
                "Transaction type not updated : db integrity error"
            )
            error_logger.error(
                "Transaction type not updated : db integrity error"
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction type not updated")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record update error")


@transaction_type_router.get(
    "/get/{transaction_type_id}", response=TransactionTypeOut
)
def get_transaction_type(request, transaction_type_id: int):
    """
    The function `get_transaction_type` retrieves the transaction type by id

    Args:
        request (HttpRequest): The HTTP request object.
        transaction_type_id (int): The id of the transaction type to retrieve.

    Returns:
        TransactionTypeOut: the transaction type object

    Raises:
        Http404: If the transaction type with the specified ID does not exist.
    """

    try:
        transaction_type = get_object_or_404(
            TransactionType, id=transaction_type_id
        )
        api_logger.debug(
            f"Transaction type retrieved : {transaction_type.transaction_type}"
        )
        return transaction_type
    except Http404:
        raise HttpError(404, "Transaction type not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction type not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@transaction_type_router.get("/list", response=List[TransactionTypeOut])
def list_transaction_types(request):
    """
    The function `list_transaction_types` retrieves a list of transaction types,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        TransactionTypeOut: a list of transaction type objects
    """

    try:
        qs = TransactionType.objects.all().order_by("id")
        api_logger.debug("Transaction type list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction type list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@transaction_type_router.delete("/delete/{transaction_type_id}")
def delete_transaction_type(request, transaction_type_id: int):
    """
    The function `delete_transaction_type` deletes the transaction type specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        transaction_type_id (int): the id of the transaction type to delete

    Returns:
        success: True

    Raises:
        Http404: If the transaction type with the specified ID does not exist.
    """

    try:
        transaction_type = get_object_or_404(
            TransactionType, id=transaction_type_id
        )
        transaction_type_name = transaction_type.transaction_type
        transaction_type.delete()
        api_logger.info(f"Transaction type deleted : {transaction_type_name}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Transaction type not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction type not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
