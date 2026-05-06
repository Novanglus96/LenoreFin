from ninja import Router
from ninja.errors import HttpError
from tags.api.schemas.graph_by_tags import GraphOut, PieGraphItem
from tags.services.tag_graph import get_graph_new_data, get_graph_data
from typing import List
import logging

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

graph_by_tags_router = Router(tags=["Graph By Tags"])


@graph_by_tags_router.get("/new", response=List[PieGraphItem])
def get_graph_new(request, widget_id: int):
    """
    The function `get_graph_new` retrieves graph data for tags for widget id.

    Args:
        request (HttpRequest): The HTTP request object.
        widget_id (int): The widget for graph data

    Returns:
        List[PieGraphItem]: the pie graph data items
    """
    try:
        result = get_graph_new_data(widget_id)
        api_logger.debug(f"Graph data retrieved : {widget_id}")
        return result
    except Exception as e:
        api_logger.error("Graph data not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@graph_by_tags_router.get("/get", response=GraphOut)
def get_graph(request, widget_id: int):
    """
    The function `get_graph` retrieves graph data for tags for widget id.

    Args:
        request (HttpRequest): The HTTP request object.
        widget_id (int): The widget for graph data

    Returns:
        GraphOut: the graph data object
    """
    try:
        result = get_graph_data(widget_id)
        api_logger.debug(f"Graph data retrieved : {widget_id}")
        return result
    except Exception as e:
        api_logger.error("Graph data not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")
