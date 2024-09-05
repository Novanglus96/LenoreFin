from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from planning.models import CalculationRule
from planning.api.schemas.calculator import (
    CalculationRuleIn,
    CalculationRuleOut,
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

calculator_router = Router(tags=["Calculator"])


@calculator_router.post("/calculation_rule/create")
def create_calculation_rule(request, payload: CalculationRuleIn):
    """
    The function `create_calculation_rule` creates a calculation
    rule.

    Args:
        request ():
        payload (CalculationRuleIn): An object using schema of CalculationRuleIn.

    Returns:
        id: returns the id of the created calculation rule
    """

    try:
        calculation_rule = CalculationRule.objects.create(**payload.dict())
        logToDB(
            f"Calculation rule created : {calculation_rule.name}",
            None,
            None,
            None,
            3001005,
            2,
        )
        return {"id": calculation_rule.id}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Calculation rule not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@calculator_router.put("/calculation_rule/update/{calculation_rule_id}")
def update_calculation_rule(
    request, calculation_rule_id: int, payload: CalculationRuleIn
):
    """
    The function `update_calculation_rule` updates the calculation rule specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        calculation_rule_id (int): the id of the calculation rule to update
        payload (CalculationRuleIn): a calculation rule object

    Returns:
        success: True

    Raises:
        Http404: If the calculation rule with the specified ID does not exist.
    """

    try:
        calculation_rule = get_object_or_404(
            CalculationRule, id=calculation_rule_id
        )
        calculation_rule.tag_ids = payload.tag_ids
        calculation_rule.name = payload.name
        calculation_rule.source_account_id = payload.source_account_id
        calculation_rule.destination_account_id = payload.destination_account_id
        calculation_rule.save()
        logToDB(
            f"Calculation rule updated : #{calculation_rule_id}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Calculation rule not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@calculator_router.delete("/calculation_rule/delete/{calculation_rule_id}")
def delete_calculation_rule(request, calculation_rule_id: int):
    """
    The function `delete_calculation_rule` deletes the calculation rule specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        calculation_rule_id (int): the id of the calculation rule to delete

    Returns:
        success: True

    Raises:
        Http404: If the calculation rule with the specified ID does not exist.
    """

    try:
        calculation_rule = get_object_or_404(
            CalculationRule, id=calculation_rule_id
        )
        rule_name = calculation_rule.name
        calculation_rule.delete()
        logToDB(
            f"Calculation rule deleted: {rule_name}",
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
            f"Calculation rule not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")
