from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from tags.models import SubTag
from tags.api.schemas.sub_tag import SubTagIn, SubTagOut
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

sub_tag_router = Router(tags=["Sub Tags"])


@sub_tag_router.get("/get/{subtag_id}", response=SubTagOut)
def get_subtag(request, subtag_id: int):
    """
    The function `get_subtag` retrieves the sub tag by id

    Args:
        request (HttpRequest): The HTTP request object.
        subtag_id (int): The id of the tag to retrieve.

    Returns:
        SubTagOut: the tag object

    Raises:
        Http404: If the sub tag with the specified ID does not exist.
    """

    try:
        subtag = get_object_or_404(SubTag, id=subtag_id)
        logToDB(
            f"Sub Tag retrieved : {subtag.tag_name}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return subtag
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Sub Tag not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@sub_tag_router.get("/list", response=List[SubTagOut])
def list_subtags(
    request,
    tag_type: Optional[int] = Query(None),
    parent: Optional[int] = Query(None),
):
    """
    The function `list_subtags` retrieves a list of subtags,
    optionally filtered by tag type or parent.

    Args:
        request (HttpRequest): The HTTP request object.
        tag_type (int): Optional tag type id to filter tags.
        parent (int): Optional filter on parent

    Returns:
        SubTagOut: a list of subtag objects
    """
    try:
        # Retrive a list of  sub tags
        qs = SubTag.objects.all()

        # Filter sub tags by tag type if a tag type is specified
        if tag_type is not None:
            qs = qs.filter(tag_type__id=tag_type)

        # Filter sub tags by parent if a parent id is specified
        if parent is not None:
            qs = qs.filter(parent__id=parent).exclude(tag_type__id=3)

        # Order tags tag_name
        qs = qs.order_by("tag_name")
        logToDB(
            "Sub Tag list retrieved",
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
            f"Sub Tag list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, f"Record retrieval error: {str(e)}")
