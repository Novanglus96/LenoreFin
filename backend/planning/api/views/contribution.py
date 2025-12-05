from ninja import Router
from django.db import IntegrityError
from ninja.errors import HttpError
from planning.models import Contribution
from planning.api.schemas.contribution import (
    ContributionIn,
    ContributionOut,
    ContributionWithTotals,
)
from django.shortcuts import get_object_or_404
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

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
        api_logger.info(f"Contribution created : {payload.contribution}")
        return {"id": contribution.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Contribution not created : contribution exists ({payload.contribution})"
            )
            error_logger.error(
                f"Contribution not created : contribution exists ({payload.contribution})"
            )
            raise HttpError(400, "Conitribution already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Contribution not created : db integrity error")
            error_logger.error("Contribution not created : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Contribution not created")
        error_logger.error(f"{str(e)}")
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
        api_logger.info(f"Contribution updated : {contribution.contribution}")
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Contribution not updated : contribution exists ({payload.contribution})"
            )
            error_logger.error(
                f"Contribution not updated : contribution exists ({payload.contribution})"
            )
            raise HttpError(400, "Contribution already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Contribution not updated : db integrity error")
            error_logger.error("Contribution not updated : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Contribution not updated")
        error_logger.error(f"{str(e)}")
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
        api_logger.debug(
            f"Contribution retrieved : {contribution.contribution}"
        )
        return contribution
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Contribution not retrieved")
        error_logger.error(f"{str(e)}")
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
        qs = Contribution.objects.all().order_by("-active", "id")
        active_contribs = qs.filter(active=True)

        # Compute totals (this can be customized based on your business logic)
        per_paycheck_total = sum(
            [contrib.per_paycheck for contrib in active_contribs]
        )
        emergency_paycheck_total = sum(
            [contrib.emergency_amt for contrib in active_contribs]
        )
        total_emergency = sum(
            [contrib.emergency_diff for contrib in active_contribs]
        )

        # Create the ContributionWithTotals object
        contributions_with_totals = ContributionWithTotals(
            contributions=list(qs),
            per_paycheck_total=per_paycheck_total,
            emergency_paycheck_total=emergency_paycheck_total,
            total_emergency=total_emergency,
        )
        api_logger.debug("Contribution list retrieved")
        return contributions_with_totals
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Contribution list not retrieved")
        error_logger.error(f"{str(e)}")
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
        api_logger.info(f"Contribution deleted : {contribution_name}")
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Contribution not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
