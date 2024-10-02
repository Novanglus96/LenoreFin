from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from planning.models import Contribution
from planning.api.schemas.contribution import (
    ContributionIn,
    ContributionOut,
    ContributionWithTotals,
)
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

contribution_router = Router(tags=["Contributions"])


@contribution_router.post("/create")
def create_contribution(request, payload: ContributionIn):
    """
    The function `create_contribution` creates a contribution

    Args:
        request ():
        payload (ContributionIn): An object using schema of ContributionIn.

    Returns:
        id: returns the id of the created contribution
    """

    try:
        contribution = Contribution.objects.create(**payload.dict())
        logToDB(
            f"Contribution created : {payload.contribution}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": contribution.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Contribution not created : contribution exists ({payload.contribution})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Conitribution already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Contribution not created : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@contribution_router.put("/update/{contribution_id}")
def update_contribution(request, contribution_id: int, payload: ContributionIn):
    """
    The function `update_contribution` updates the contribution specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        contribution_id (int): the id of the contribution to update
        payload (ContributionIn): a contribution object

    Returns:
        success: True

    Raises:
        Http404: If the contribution with the specified ID does not exist.
    """

    try:
        contribution = get_object_or_404(Contribution, id=contribution_id)
        contribution.contribution = payload.contribution
        contribution.per_paycheck = payload.per_paycheck
        contribution.emergency_amt = payload.emergency_amt
        contribution.emergency_diff = payload.emergency_diff
        contribution.cap = payload.cap
        contribution.active = payload.active
        contribution.save()
        logToDB(
            f"Contribution updated : {contribution.contribution}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Contribution not updated : contribution exists ({payload.contribution})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Contribution already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Contribution not updated : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@contribution_router.get("/get/{contribution_id}", response=ContributionOut)
def get_contribution(request, contribution_id: int):
    """
    The function `get_contribution` retrieves the contribution by id

    Args:
        request (HttpRequest): The HTTP request object.
        contribution_id (int): The id of the contribution to retrieve.

    Returns:
        ContributionOut: the contribution object

    Raises:
        Http404: If the contribution with the specified ID does not exist.
    """

    try:
        contribution = get_object_or_404(Contribution, id=contribution_id)
        logToDB(
            f"Contribution retrieved : {contribution.contribution}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return contribution
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@contribution_router.get("/list", response=ContributionWithTotals)
def list_contributions(request):
    """
    The function `list_contributions` retrieves a list of contributions,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        ContributionOut: a list of contribution objects
    """

    try:
        qs = Contribution.objects.all().order_by("id")

        # Compute totals (this can be customized based on your business logic)
        per_paycheck_total = sum([contrib.per_paycheck for contrib in qs])
        emergency_paycheck_total = sum(
            [contrib.emergency_amt for contrib in qs]
        )
        total_emergency = sum([contrib.emergency_diff for contrib in qs])

        # Create the ContributionWithTotals object
        contributions_with_totals = ContributionWithTotals(
            contributions=list(qs),
            per_paycheck_total=per_paycheck_total,
            emergency_paycheck_total=emergency_paycheck_total,
            total_emergency=total_emergency,
        )
        logToDB(
            "Contribution list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return contributions_with_totals
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@contribution_router.delete("/delete/{contribution_id}")
def delete_contribution(request, contribution_id: int):
    """
    The function `delete_contribution` deletes the contribution specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        contribution_id (int): the id of the contribution to delete

    Returns:
        success: True

    Raises:
        Http404: If the contribution with the specified ID does not exist.
    """

    try:
        contribution = get_object_or_404(Contribution, id=contribution_id)
        contribution_name = contribution.contribution
        contribution.delete()
        logToDB(
            f"Contribution deleted : {contribution_name}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")
