from ninja import Router, Query
from ninja.errors import HttpError
from tags.models import MainTag
from tags.api.schemas.main_tag import MainTagOut, MainTagQuery
from django.shortcuts import get_object_or_404
from typing import List
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

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
        api_logger.debug(f"Main Tag retrieved : {maintag.tag_name}")
        return maintag
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Main Tag not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@main_tag_router.get("/list", response=List[MainTagOut])
def list_maintags(
    request,
    query: MainTagQuery = Query(...),
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
        if query.tag_type is not None:
            qs = qs.filter(tag_type__id=query.tag_type)

        # Order tags by tag_name
        qs = qs.order_by("tag_name")
        api_logger.debug("Main Tag list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Main Tag list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")
