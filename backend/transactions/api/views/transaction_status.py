from ninja import Router
from django.db import IntegrityError
from ninja.errors import HttpError
from transactions.models import TransactionStatus
from transactions.api.schemas.transaction_status import (
    TransactionStatusIn,
    TransactionStatusOut,
)
from django.shortcuts import get_object_or_404
from django.http import Http404
from typing import List
import logging
from administration.api.dependencies.auth import FullAccessAuth

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

transaction_status_router = Router(tags=["Transaction Statuses"])


@transaction_status_router.put("/update/{transactionstatus_id}", auth=FullAccessAuth())
def update_transaction_status(
    request, transactionstatus_id: int, payload: TransactionStatusIn
):
    """
    The function `update_transaction_status` updates the transaction status specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        transactionsatus_id (int): the id of the transaction status to update
        payload (TransactionStatusIn): a transaction status object

    Returns:
        success: True

    Raises:
        Http404: If the transaction status with the specified ID does not exist.
    """

    try:
        transaction_status = get_object_or_404(
            TransactionStatus, id=transactionstatus_id
        )
        transaction_status.transaction_status = payload.transaction_status
        transaction_status.save()
        api_logger.info(
            f"Transaction status updated : {transaction_status.transaction_status}"
        )
        return {"success": True}
    except Http404:
        raise HttpError(404, "Transaction status not found")
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Transaction status not updated : transaction status exists ({payload.transaction_status})"
            )
            error_logger.error(
                f"Transaction status not updated : transaction status exists ({payload.transaction_status})"
            )
            raise HttpError(400, "Transaction status already exists")
        else:
            # Log other types of integry errors
            api_logger.error(
                "Transaction status not updated : db integrity error"
            )
            error_logger.error(
                "Transaction status not updated : db integrity error"
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction status not updated")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record update error")


@transaction_status_router.get(
    "/get/{transactionstatus_id}",
    response=TransactionStatusOut,
)
def get_transaction_status(request, transactionstatus_id: int):
    """
    The function `get_transaction_status` retrieves the transaction status by id

    Args:
        request (HttpRequest): The HTTP request object.
        transactionstatus_id (int): The id of the transaction status to retrieve.

    Returns:
        TransactionStatusOut: the transaction status object

    Raises:
        Http404: If the transaction status with the specified ID does not exist.
    """

    try:
        transaction_status = get_object_or_404(
            TransactionStatus, id=transactionstatus_id
        )
        api_logger.debug(
            f"Transaction status retrieved : {transaction_status.transaction_status}"
        )
        return transaction_status
    except Http404:
        raise HttpError(404, "Transaction status not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction status not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@transaction_status_router.get("/list", response=List[TransactionStatusOut])
def list_transaction_statuses(request):
    """
    The function `list_transaction_statuses` retrieves a list of transaction statuses,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        TransactionStatusOut: a list of transaction status objects
    """

    try:
        qs = TransactionStatus.objects.all().order_by("id")
        api_logger.debug("Transaction status list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction status list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@transaction_status_router.delete("/delete/{transactionstatus_id}", auth=FullAccessAuth())
def delete_transaction_status(request, transactionstatus_id: int):
    """
    The function `delete_transaction_status` deletes the transaction status specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        transactionstatus_id (int): the id of the transaction status to delete

    Returns:
        success: True

    Raises:
        Http404: If the transaction status with the specified ID does not exist.
    """

    try:
        transaction_status = get_object_or_404(
            TransactionStatus, id=transactionstatus_id
        )
        transaction_status_name = transaction_status.transaction_status
        transaction_status.delete()
        api_logger.info(
            f"Transaction status deleted : {transaction_status_name}"
        )
        return {"success": True}
    except Http404:
        raise HttpError(404, "Transaction status not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction status not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
