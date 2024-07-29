from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from administration.models import ErrorLevel
from administration.api.schemas.error_level import ErrorLevelIn, ErrorLevelOut
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

error_level_router = Router(tags=["Error Levels"])


@error_level_router.put("/update/{errorlevel_id}")
def update_errorlevel(request, errorlevel_id: int, payload: ErrorLevelIn):
    """
    The function `update_errorlevel` updates the error level specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        errorlevel_id (int): the id of the error level to update
        payload (ErrorLevelIn): an error level object

    Returns:
        success: True

    Raises:
        Http404: If the error level with the specified ID does not exist.
    """

    try:
        errorlevel = get_object_or_404(ErrorLevel, id=errorlevel_id)
        errorlevel.error_level = payload.error_level
        errorlevel.save()
        logToDB(
            f"Error level updated : {errorlevel.error_level}",
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
                f"Error level not updated : error level exists ({payload.error_level})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Error level already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Error level not updated : db integrity error",
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
            f"Error level not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@error_level_router.get("/get/{errorlevel_id}", response=ErrorLevelOut)
def get_errorlevel(request, errorlevel_id: int):
    """
    The function `get_errorlevel` retrieves the error level by id

    Args:
        request (HttpRequest): The HTTP request object.
        errorlevel_id (int): The id of the error level to retrieve.

    Returns:
        ErrorLevelOut: the error level object

    Raises:
        Http404: If the error level with the specified ID does not exist.
    """

    try:
        errorlevel = get_object_or_404(ErrorLevel, id=errorlevel_id)
        logToDB(
            f"Error level retrieved : {errorlevel.error_level}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return errorlevel
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Error level not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@error_level_router.get("/list", response=List[ErrorLevelOut])
def list_errorlevels(request):
    """
    The function `list_errorlevels` retrieves a list of error levels,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        ErrorLevelOut: a list of error level objects
    """

    try:
        qs = ErrorLevel.objects.all().order_by("id")
        logToDB(
            "Error level list retrieved",
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
            f"Error level list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@error_level_router.delete("/delete/{errorlevel_id}")
def delete_errorlevel(request, errorlevel_id: int):
    """
    The function `delete_errorlevel` deletes the error level specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        errorlevel_id (int): the id of the error level to delete

    Returns:
        success: True

    Raises:
        Http404: If the error level with the specified ID does not exist.
    """

    try:
        errorlevel = get_object_or_404(ErrorLevel, id=errorlevel_id)
        error_name = errorlevel.error_level
        errorlevel.delete()
        logToDB(
            f"Error level deleted : {error_name}",
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
            f"Error level not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")
