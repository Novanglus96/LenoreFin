from ninja import Router
from ninja.errors import HttpError
from administration.models import DescriptionHistory
from administration.api.schemas.description_history import DescriptionHistoryOut
from typing import List
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

description_history_router = Router(tags=["Description Histories"])


@description_history_router.get("/list", response=List[DescriptionHistoryOut])
def list_description_histories(request):
    """
    The function `list_description_histories` retrieves a list of description
    histories

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        List[DescriptionHistoryOut]: a list of description histories
    """

    try:
        qs = DescriptionHistory.objects.all().order_by("description_normalized")
        qs = list(qs)
        api_logger.debug("Description Histories retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Description Histories not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
