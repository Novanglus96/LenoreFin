from ninja import Router
from ninja.errors import HttpError
from transactions.models import TransactionDetail
from transactions.api.schemas.transaction_detail import (
    TransactionDetailOut,
    TransactionDetailIn,
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

transaction_detail_router = Router(tags=["Transaction Details"])


@transaction_detail_router.get(
    "/get/{transactiondetail_id}",
    response=TransactionDetailOut,
)
def get_transaction_detail(request, transactiondetail_id: int):
    """
    The function `get_transaction_detail` retrieves the transaction detail by id

    Args:
        request (HttpRequest): The HTTP request object.
        transactiondetail_id (int): The id of the transaction detail to retrieve.

    Returns:
        TransactionDetailOut: the transaction detail object

    Raises:
        Http404: If the transaction detail with the specified ID does not exist.
    """

    try:
        transaction_detail = get_object_or_404(
            TransactionDetail, id=transactiondetail_id
        )
        api_logger.debug(
            f"Transaction detail retrieved : #{transaction_detail.id}"
        )
        return transaction_detail
    except Http404:
        raise HttpError(404, "Transaction detail not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction detail not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@transaction_detail_router.get("/list", response=List[TransactionDetailOut])
def list_transactiondetails(request):
    """
    The function `list_transactiondetails` retrieves a list of transaction details,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        TransactionDetailOut: a list of transaction detail objects
    """

    try:
        qs = TransactionDetail.objects.all().order_by("id")
        api_logger.debug("Transaction detail list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction detail list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@transaction_detail_router.delete("/delete/{transactiondetail_id}", auth=FullAccessAuth())
def delete_transaction_detail(request, transactiondetail_id: int):
    """
    The function `delete_transaction_detail` deletes the transaction detail specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        transactiondetail_id (int): the id of the transaction detail to delete

    Returns:
        success: True

    Raises:
        Http404: If the transaction detail with the specified ID does not exist.
    """

    try:
        transaction_detail = get_object_or_404(
            TransactionDetail, id=transactiondetail_id
        )
        transaction_detail.delete()
        api_logger.info(f"Transaction detail deleted : #{transactiondetail_id}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Transaction detail not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction detail not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@transaction_detail_router.post("/create", auth=FullAccessAuth())
def create_transaction_detail(request, payload: TransactionDetailIn):
    """
    The function `create_transaction_detail` creates a transaction detail

    Args:
        request ():
        payload (TransactionDetailIn): An object using schema of TransactionDetailIn.

    Returns:
        id: returns the id of the created transaction detail
    """

    try:
        data = payload.dict()
        data.pop("account_id", None)
        transaction_detail = TransactionDetail.objects.create(**data)
        api_logger.info(
            f"Transaction detail created : #{transaction_detail.transaction.id}"
        )
        return {"id": transaction_detail.id}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction detail not created")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record creation error")


@transaction_detail_router.put("/update/{transactiondetail_id}", auth=FullAccessAuth())
def update_transaction_detail(
    request, transactiondetail_id: int, payload: TransactionDetailIn
):
    """
    The function `update_transaction_detail` updates the transacion detail specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        transactiondetail_id (int): the id of the transaction detail to update
        payload (TransactionDetailIn): a transaction detail object

    Returns:
        success: True

    Raises:
        Http404: If the transaction detail with the specified ID does not exist.
    """

    try:
        transaction_detail = get_object_or_404(
            TransactionDetail, id=transactiondetail_id
        )
        transaction_detail.transaction_id = payload.transaction_id
        transaction_detail.account_id = payload.account_id
        transaction_detail.detail_amt = payload.detail_amt
        transaction_detail.tag_id = payload.tag_id
        transaction_detail.full_toggle = payload.full_toggle
        transaction_detail.save()
        api_logger.info(f"Transaction detail updated : #{transactiondetail_id}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Transaction detail not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction detail not updated")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record update error")
