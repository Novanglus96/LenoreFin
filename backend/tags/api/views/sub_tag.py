from ninja import Router, Query
from ninja.errors import HttpError
from tags.models import SubTag
from tags.api.schemas.sub_tag import SubTagOut, SubTagQuery
from django.shortcuts import get_object_or_404
from django.http import Http404
from typing import List
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

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
        api_logger.debug(f"Sub Tag retrieved : {subtag.tag_name}")
        return subtag
    except Http404:
        raise HttpError(404, "Sub Tag not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Sub Tag not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@sub_tag_router.get("/list", response=List[SubTagOut])
def list_subtags(request, query: SubTagQuery = Query(...)):
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
        if query.tag_type is not None:
            qs = qs.filter(tag_type__id=query.tag_type)

        # Filter sub tags by parent if a parent id is specified
        if query.parent is not None:
            qs = qs.filter(parent__id=query.parent).exclude(tag_type__id=3)

        # Order tags tag_name
        qs = qs.order_by("tag_name")
        api_logger.debug("Sub Tag list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Sub Tag list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")
