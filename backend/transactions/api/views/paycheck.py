from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from transactions.models import Paycheck
from transactions.api.schemas.paycheck import PaycheckIn, PaycheckOut
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
        logToDB(
            f"Paycheck created : #{paycheck.id}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": paycheck.id}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Paycheck not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
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
        logToDB(
            f"Paycheck updated : #{paycheck_id}",
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
            f"Paycheck not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
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
        logToDB(
            f"Paycheck retrieved : #{paycheck.id}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return paycheck
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Paycheck not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
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
        logToDB(
            "Paycheck list retrieved",
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
            f"Paycheck list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
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
        logToDB(
            f"Paycheck deleted : {paycheck_id}",
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
            f"Paycheck not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")
