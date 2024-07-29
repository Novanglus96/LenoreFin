from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from transactions.models import TransactionType
from transactions.api.schemas.transaction_type import (
    TransactionTypeIn,
    TransactionTypeOut,
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
        logToDB(
            f"Transaction type updated : {transaction_type.transaction_type}",
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
                f"Transaction type not updated : transaction type exists ({payload.transaction_type})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Transaction type already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Transaction type not updated : db integrity error",
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
            f"Transaction type not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
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
        logToDB(
            f"Transaction type retrieved : {transaction_type.transaction_type}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return transaction_type
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction type not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
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
        logToDB(
            "Transaction type list retrieved",
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
            f"Transaction type list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
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
        logToDB(
            f"Transaction type deleted : {transaction_type_name}",
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
            f"Transaction type not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")
