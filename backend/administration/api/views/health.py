from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
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

health_router = Router(tags=["Health"])


@health_router.get("/")
def health_check(request):
    """
    The function `health_check` returns ok if backend is ready.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        status (str): returns ok when backend is up
    """
    return {"status": "ok"}
