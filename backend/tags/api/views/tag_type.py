from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from tags.models import TagType
from tags.api.schemas.tag_type import TagTypeIn, TagTypeOut
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


tag_type_router = Router(tags=["Tag Types"])


@tag_type_router.get("/tagtypes", response=List[TagTypeOut])
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
        qs = TagType.objects.exclude(id=3).order_by("id")
        logToDB(
            "Tag type list retrieved",
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
            f"Tag type list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")
