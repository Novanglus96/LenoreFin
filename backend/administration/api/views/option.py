from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from administration.models import Option
from administration.api.schemas.option import OptionIn, OptionOut
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

option_router = Router(tags=["Options"])


@option_router.patch("/update/{option_id}")
def update_option(request, option_id: int, payload: OptionIn):
    """
    The function `update_option` updates the option specified by id,
    patching the option if a field is sent in the payload.

    Args:
        request (HttpRequest): The HTTP request object.
        option_id (int): the id of the option to update
        payload (OptionIn): an option object

    Returns:
        success: True

    Raises:
        Http404: If the option with the specified ID does not exist.
    """

    try:
        option = get_object_or_404(Option, id=option_id)
        if payload.log_level_id is not None:
            option.log_level_id = payload.log_level_id
        if payload.alert_balance is not None:
            option.alert_balance = payload.alert_balance
        if payload.alert_period is not None:
            option.alert_period = payload.alert_period
        if payload.widget1_graph_name is not None:
            option.widget1_graph_name = payload.widget1_graph_name
        if payload.widget1_tag_id is not None:
            option.widget1_tag_id = payload.widget1_tag_id
        if payload.widget1_type_id is not None:
            option.widget1_type_id = payload.widget1_type_id
        if payload.widget1_month is not None:
            option.widget1_month = payload.widget1_month
        if payload.widget1_exclude is not None:
            option.widget1_exclude = payload.widget1_exclude
        if payload.widget2_graph_name is not None:
            option.widget2_graph_name = payload.widget2_graph_name
        if payload.widget2_tag_id is not None:
            option.widget2_tag_id = payload.widget2_tag_id
        if payload.widget2_type_id is not None:
            option.widget2_type_id = payload.widget2_type_id
        if payload.widget2_month is not None:
            option.widget2_month = payload.widget2_month
        if payload.widget2_exclude is not None:
            option.widget2_exclude = payload.widget2_exclude
        if payload.widget3_graph_name is not None:
            option.widget3_graph_name = payload.widget3_graph_name
        if payload.widget3_tag_id is not None:
            option.widget3_tag_id = payload.widget3_tag_id
        if payload.widget3_type_id is not None:
            option.widget3_type_id = payload.widget3_type_id
        if payload.widget3_month is not None:
            option.widget3_month = payload.widget3_month
        if payload.widget3_exclude is not None:
            option.widget3_exclude = payload.widget3_exclude
        if payload.auto_archive is not None:
            option.auto_archive = payload.auto_archive
        if payload.enable_cc_bill_calculation is not None:
            option.enable_cc_bill_calculation = (
                payload.enable_cc_bill_calculation
            )
        if payload.report_main is not None:
            option.report_main = payload.report_main
        if payload.report_individual is not None:
            option.report_individual = payload.report_individual
        option.save()
        logToDB(
            f"Option updated : {option_id}",
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
            f"Option not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@option_router.get("/get/{option_id}", response=OptionOut)
def get_option(request, option_id: int):
    """
    The function `get_option` retrieves the option by id

    Args:
        request (HttpRequest): The HTTP request object.
        option_id (int): The id of the option to retrieve.

    Returns:
        OptionOut: the option object

    Raises:
        Http404: If the option with the specified ID does not exist.
    """

    try:
        option = get_object_or_404(Option, id=option_id)
        logToDB(
            f"Option retrieved : #{option.id}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return option
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Option not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@option_router.get("/list", response=List[OptionOut])
def list_options(request):
    """
    The function `list_options` retrieves a list of options,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        OptionOut: a list of option objects
    """

    try:
        qs = Option.objects.all().order_by("id")
        logToDB(
            "Option list retrieved",
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
            f"Option list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@option_router.delete("/delete/{option_id}")
def delete_option(request, option_id: int):
    """
    The function `delete_option` deletes the option specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        option_id (int): the id of the option to delete

    Returns:
        success: True

    Raises:
        Http404: If the option with the specified ID does not exist.
    """

    try:
        option = get_object_or_404(Option, id=option_id)
        option.delete()
        logToDB(
            f"Option deleted : #{option_id}",
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
            f"Option not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")
