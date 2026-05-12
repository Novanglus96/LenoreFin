from ninja import Router
from django.db import IntegrityError
from ninja.errors import HttpError
from planning.models import ContribRule
from planning.api.schemas.contrib_rule import ContribRuleIn, ContribRuleOut
from django.shortcuts import get_object_or_404
from django.http import Http404
from typing import List
import logging
from administration.api.dependencies.auth import FullAccessAuth

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

contrib_rule_router = Router(tags=["Contribution Rules"])


@contrib_rule_router.post("/create", auth=FullAccessAuth())
def create_contrib_rule(request, payload: ContribRuleIn):
    """
    The function `create_contrib_rule` creates a contribution rule

    Args:
        request ():
        payload (ContribRuleIn): An object using schema of ContribRuleIn.

    Returns:
        id: returns the id of the created contribution rule
    """

    try:
        contrib_rule = ContribRule.objects.create(**payload.dict())
        api_logger.info(f"Contribution rule created : {payload.rule}")
        return {"id": contrib_rule.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Contribution rule not created : rule exists ({payload.rule})"
            )
            error_logger.error(
                f"Contribution rule not created : rule exists ({payload.rule})"
            )
            raise HttpError(400, "Conitribution rule already exists")
        else:
            # Log other types of integry errors
            api_logger.error(
                "Contribution rule not created : db integrity error"
            )
            error_logger.error(
                "Contribution rule not created : db integrity error"
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Contribution rule not created")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record creation error: {str(e)}")


@contrib_rule_router.put("/update/{contribrule_id}", auth=FullAccessAuth())
def update_contrib_rule(request, contribrule_id: int, payload: ContribRuleIn):
    """
    The function `update_contrib_rule` updates the contribution rule specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        contribrule_id (int): the id of the contribution rule to update
        payload (ContribRuleIn): a contribution rule object

    Returns:
        success: True

    Raises:
        Http404: If the contribution rule with the specified ID does not exist.
    """

    try:
        contrib_rule = get_object_or_404(ContribRule, id=contribrule_id)
        contrib_rule.rule = payload.rule
        contrib_rule.cap = payload.cap
        contrib_rule.order = payload.order
        contrib_rule.save()
        api_logger.info(f"Contribution rule updated : {contrib_rule.rule}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Contribution rule not found")
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Contribution rule not updated : contribution rule exists ({payload.rule})"
            )
            error_logger.error(
                f"Contribution rule not updated : contribution rule exists ({payload.rule})"
            )
            raise HttpError(400, "Contribution rule already exists")
        else:
            # Log other types of integry errors
            api_logger.error(
                "Contribution rule not updated : db integrity error"
            )
            error_logger.error(
                "Contribution rule not updated : db integrity error"
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Contribution rule not updated")
        task_logger.error(f"{str(e)}")
        raise HttpError(500, "Record update error")


@contrib_rule_router.get("/get/{contribrule_id}", response=ContribRuleOut)
def get_contribrule(request, contribrule_id: int):
    """
    The function `get_contribrule` retrieves the contribution rule by id

    Args:
        request (HttpRequest): The HTTP request object.
        contribrule_id (int): The id of the contribution rule to retrieve.

    Returns:
        ContribRuleOut: the contribution rule object

    Raises:
        Http404: If the contribution rule with the specified ID does not exist.
    """

    try:
        contrib_rule = get_object_or_404(ContribRule, id=contribrule_id)
        api_logger.debug(f"Contribution rule retrieved : {contrib_rule.rule}")
        return contrib_rule
    except Http404:
        raise HttpError(404, "Contribution rule not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Contribution rule not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@contrib_rule_router.get("/list", response=List[ContribRuleOut])
def list_contrib_rules(request):
    """
    The function `list_contrib_rules` retrieves a list of contribution rules,
    orderd by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        ContribRuleOut: a list of contribution rule objects
    """

    try:
        qs = ContribRule.objects.all().order_by("order", "id")
        api_logger.debug("Contribution rule list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Contribution rule list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@contrib_rule_router.delete("/delete/{contribrule_id}", auth=FullAccessAuth())
def delete_contrib_rule(request, contribrule_id: int):
    """
    The function `delete_contrib_rule` deletes the contribution rule specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        contribrule_id (int): the id of the contribution rule to delete

    Returns:
        success: True

    Raises:
        Http404: If the contribution rule with the specified ID does not exist.
    """

    try:
        contrib_rule = get_object_or_404(ContribRule, id=contribrule_id)
        rule_name = contrib_rule.rule
        contrib_rule.delete()
        api_logger.info(f"Contribtion rule deleted : {rule_name}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Contribution rule not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Contribution rule not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
