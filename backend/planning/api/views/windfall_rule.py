from ninja import Router
from django.db import IntegrityError
from ninja.errors import HttpError
from planning.models import WindfallRule
from planning.api.schemas.windfall_rule import WindfallRuleIn, WindfallRuleOut
from django.shortcuts import get_object_or_404
from django.http import Http404
from typing import List
import logging
from administration.api.dependencies.auth import FullAccessAuth

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

windfall_rule_router = Router(tags=["Windfall Rules"])


@windfall_rule_router.post("/create", auth=FullAccessAuth())
def create_windfall_rule(request, payload: WindfallRuleIn):
    """
    The function `create_windfall_rule` creates a windfall rule

    Args:
        request ():
        payload (WindfallRuleIn): An object using schema of WindfallRuleIn.

    Returns:
        id: returns the id of the created windfall rule
    """

    try:
        windfall_rule = WindfallRule.objects.create(**payload.dict())
        api_logger.info(f"Windfall rule created : {payload.rule}")
        return {"id": windfall_rule.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Windfall rule not created : rule exists ({payload.rule})"
            )
            error_logger.exception(
                f"Windfall rule not created : rule exists ({payload.rule})"
            )
            raise HttpError(400, "Conitribution rule already exists")
        else:
            # Log other types of integry errors
            api_logger.error(
                "Windfall rule not created : db integrity error"
            )
            error_logger.exception(
                "Windfall rule not created : db integrity error"
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Windfall rule not created")
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, f"Record creation error: {str(e)}")


@windfall_rule_router.put("/update/{windfall_rule_id}", auth=FullAccessAuth())
def update_windfall_rule(request, windfall_rule_id: int, payload: WindfallRuleIn):
    """
    The function `update_windfall_rule` updates the windfall rule specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        windfall_rule_id (int): the id of the windfall rule to update
        payload (WindfallRuleIn): a windfall rule object

    Returns:
        success: True

    Raises:
        Http404: If the windfall rule with the specified ID does not exist.
    """

    try:
        windfall_rule = get_object_or_404(WindfallRule, id=windfall_rule_id)
        windfall_rule.rule = payload.rule
        windfall_rule.cap = payload.cap
        windfall_rule.order = payload.order
        windfall_rule.save()
        api_logger.info(f"Windfall rule updated : {windfall_rule.rule}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Windfall rule not found")
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Windfall rule not updated : windfall rule exists ({payload.rule})"
            )
            error_logger.exception(
                f"Windfall rule not updated : windfall rule exists ({payload.rule})"
            )
            raise HttpError(400, "Windfall rule already exists")
        else:
            # Log other types of integry errors
            api_logger.error(
                "Windfall rule not updated : db integrity error"
            )
            error_logger.exception(
                "Windfall rule not updated : db integrity error"
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Windfall rule not updated")
        task_logger.error(f"{str(e)}")
        raise HttpError(500, "Record update error")


@windfall_rule_router.get("/get/{windfall_rule_id}", response=WindfallRuleOut)
def get_windfall_rule(request, windfall_rule_id: int):
    """
    The function `get_windfall_rule` retrieves the windfall rule by id

    Args:
        request (HttpRequest): The HTTP request object.
        windfall_rule_id (int): The id of the windfall rule to retrieve.

    Returns:
        WindfallRuleOut: the windfall rule object

    Raises:
        Http404: If the windfall rule with the specified ID does not exist.
    """

    try:
        windfall_rule = get_object_or_404(WindfallRule, id=windfall_rule_id)
        api_logger.debug(f"Windfall rule retrieved : {windfall_rule.rule}")
        return windfall_rule
    except Http404:
        raise HttpError(404, "Windfall rule not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Windfall rule not retrieved")
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@windfall_rule_router.get("/list", response=List[WindfallRuleOut])
def list_windfall_rules(request):
    """
    The function `list_windfall_rules` retrieves a list of windfall rules,
    orderd by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        WindfallRuleOut: a list of windfall rule objects
    """

    try:
        qs = WindfallRule.objects.all().order_by("order", "id")
        api_logger.debug("Windfall rule list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Windfall rule list not retrieved")
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@windfall_rule_router.delete("/delete/{windfall_rule_id}", auth=FullAccessAuth())
def delete_windfall_rule(request, windfall_rule_id: int):
    """
    The function `delete_windfall_rule` deletes the windfall rule specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        windfall_rule_id (int): the id of the windfall rule to delete

    Returns:
        success: True

    Raises:
        Http404: If the windfall rule with the specified ID does not exist.
    """

    try:
        windfall_rule = get_object_or_404(WindfallRule, id=windfall_rule_id)
        rule_name = windfall_rule.rule
        windfall_rule.delete()
        api_logger.info(f"Windfall rule deleted : {rule_name}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Windfall rule not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Windfall rule not deleted")
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
