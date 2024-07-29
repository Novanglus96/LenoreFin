from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from transactions.models import TransactionStatus
from transactions.api.schemas.transaction_status import (
    TransactionStatusIn,
    TransactionStatusOut,
)
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

transaction_status_router = Router(tags=["Transaction Statuses"])


@transaction_status_router.put("/update/{transactionstatus_id}")
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
        logToDB(
            f"Transaction status updated : {transaction_status.transaction_status}",
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
                f"Transaction status not updated : transaction status exists ({payload.transaction_status})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Transaction status already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Transaction status not updated : db integrity error",
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
            f"Transaction status not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
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
        logToDB(
            f"Transaction status retrieved : {transaction_status.transaction_status}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return transaction_status
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction status not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
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
        logToDB(
            "Transaction status list retrieved",
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
            f"Transaction status list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@transaction_status_router.delete("/delete/{transactionstatus_id}")
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
        logToDB(
            f"Transaction status deleted : {transaction_status_name}",
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
            f"Transaction status not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")
