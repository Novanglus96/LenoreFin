from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from administration.models import Payee
from administration.api.schemas.payee import PayeeIn, PayeeOut
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

payee_router = Router(tags=["Payees"])


@payee_router.post("/create")
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
        logToDB(
            f"Payee created : {payee.payee_name}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": payee.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Payee not created : payee exists ({payload.payee_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Payee already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Payee not created : db integrity error",
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
            f"Payee not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@payee_router.put("/update/{payee_id}")
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
        logToDB(
            f"Payee updated : {payee.payee_name}",
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
                f"Payee not updated : payee exists ({payload.payee_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Payee already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Payee not updated : db integrity error",
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
            f"Payee not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
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
        logToDB(
            f"Payee retrieved : {payee.payee_name}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return payee
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Payee not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
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
        logToDB(
            "Payee list retrieved",
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
            f"Payee list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@payee_router.delete("/delete/{payee_id}")
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
        logToDB(
            f"Payee deleted : {payee_name}",
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
            f"Payee not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")
