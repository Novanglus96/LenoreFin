from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from transactions.models import TransactionDetail
from transactions.api.schemas.transaction_detail import (
    TransactionDetailOut,
    TransactionDetailIn,
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
        logToDB(
            f"Transaction detail retrieved : #{transaction_detail.id}",
            None,
            None,
            transaction_detail.transaction.id,
            3001006,
            1,
        )
        return transaction_detail
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction detail not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
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
        logToDB(
            "Transaction detail list retrieved",
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
            f"Transaction detail list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@transaction_detail_router.delete("/delete/{transactiondetail_id}")
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
        logToDB(
            f"Transaction detail deleted : #{transactiondetail_id}",
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
            f"Transaction detail not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@transaction_detail_router.post("/create")
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
        transaction_detail = TransactionDetail.objects.create(**payload.dict())
        logToDB(
            f"Transaction detail created : #{transaction_detail.transaction.id}",
            None,
            None,
            payload.transaction_id,
            3001005,
            2,
        )
        return {"id": transaction_detail.id}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction detail not created : {str(e)}",
            None,
            None,
            payload.transaction_id,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@transaction_detail_router.put("/update/{transactiondetail_id}")
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
        transaction_detail.save()
        logToDB(
            f"Transaction detail updated : #{transactiondetail_id}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction detail not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")
