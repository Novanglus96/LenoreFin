from ninja import Router
from ninja.errors import HttpError
from tags.models import TagType
from tags.api.schemas.tag_type import TagTypeOut
from typing import List
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")


tag_type_router = Router(tags=["Tag Types"])


@tag_type_router.get("/list", response=List[TagTypeOut])
def list_tag_types(request):
    """
    The function `list_tag_types` retrieves a list of tag types,
    ordered by id ascending and excluding Misc. tags (id=3)

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        TagTypeOut: a list of tag type objects
    """

    try:
        qs = TagType.objects.exclude(slug='misc').order_by("id")
        api_logger.debug("Tag type list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Tag type list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
