from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from planning.models import ContribRule
from planning.api.schemas.contrib_rule import ContribRuleIn, ContribRuleOut
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

contrib_rule_router = Router(tags=["Contribution Rules"])


@contrib_rule_router.post("/create")
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
        logToDB(
            f"Contribution rule created : {payload.rule}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": contrib_rule.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Contribution rule not created : rule exists ({payload.rule})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Conitribution rule already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Contribution rule not created : db integrity error",
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
            f"Contribution rule not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, f"Record creation error: {str(e)}")


@contrib_rule_router.put("/update/{contribrule_id}")
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
        contrib_rule.save()
        logToDB(
            f"Contribution rule updated : {contrib_rule.rule}",
            None,
            None,
            None,
            3001002,
            2,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Contribution rule not updated : contribution rule exists ({payload.rule})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Contribution rule already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Contribution rule not updated : db integrity error",
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
            f"Contribution rule not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
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
        logToDB(
            f"Contribution rule retrieved : {contrib_rule.rule}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return contrib_rule
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution rule not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
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
        qs = ContribRule.objects.all().order_by("id")
        logToDB(
            "Contribution rule list retrieved",
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
            f"Contribution rule list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@contrib_rule_router.delete("/delete/{contribrule_id}")
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
        logToDB(
            f"Contribtion rule deleted : {rule_name}",
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
            f"Contribution rule not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")
