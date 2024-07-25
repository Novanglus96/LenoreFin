from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from tags.models import MainTag
from tags.api.schemas.main_tag import MainTagIn, MainTagOut
from administration.models import logToDB
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

main_tag_router = Router(tags=["Main Tags"])


@main_tag_router.get("/get/{maintag_id}", response=MainTagOut)
def get_maintag(request, maintag_id: int):
    """
    The function `get_maintag` retrieves the main tag by id

    Args:
        request (HttpRequest): The HTTP request object.
        maintag_id (int): The id of the main tag to retrieve.

    Returns:
        MainTagOut: the main tag object

    Raises:
        Http404: If the main tag with the specified ID does not exist.
    """

    try:
        maintag = get_object_or_404(MainTag, id=maintag_id)
        logToDB(
            f"Main Tag retrieved : {maintag.tag_name}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return maintag
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Main Tag not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@main_tag_router.get("/list", response=List[MainTagOut])
def list_maintags(
    request,
    tag_type: Optional[int] = Query(None),
):
    """
    The function `list_maintags` retrieves a list of main tags,
    optionally filtered by tag type.

    Args:
        request (HttpRequest): The HTTP request object.
        tag_type (int): Optional tag type id to filter tags.

    Returns:
        MainTagOut: a list of main tag objects
    """
    try:
        # Retrive a list of main tags
        qs = MainTag.objects.all()

        # Filter main tags by tag type if a tag type is specified
        if tag_type is not None:
            qs = qs.filter(tag_type__id=tag_type)

        # Order tags by tag_name
        qs = qs.order_by("tag_name")
        logToDB(
            "Main Tag list retrieved",
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
            f"Main Tag list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, f"Record retrieval error: {str(e)}")
