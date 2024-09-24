from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from administration.models import DescriptionHistory
from administration.api.schemas.description_history import DescriptionHistoryOut
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
        logToDB(
            "Description Histories retrieved",
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
            f"Description Histories not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")
