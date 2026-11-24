import logging
from typing import List

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from administration.api.dependencies.auth import FullAccessAuth
from planning.api.schemas.windfall_rule import WindfallRuleIn, WindfallRuleOut
from planning.models import WindfallRule

api_logger = logging.getLogger("api")

windfall_rule_router = Router(tags=["Windfall Rules"])


def rule_out(rule: WindfallRule) -> WindfallRuleOut:
    return WindfallRuleOut(
        id=rule.id,
        rule=rule.rule,
        bucket_id=rule.bucket_id,
        bucket_name=rule.bucket.name if rule.bucket_id else None,
        cap=rule.cap,
        cap_amount=rule.cap_amount,
        order=rule.order,
    )


@windfall_rule_router.get("/list", response=List[WindfallRuleOut])
def list_rules(request):
    return [rule_out(r) for r in WindfallRule.objects.select_related("bucket")]


@windfall_rule_router.post("/create", auth=FullAccessAuth())
def create_rule(request, payload: WindfallRuleIn):
    try:
        rule = WindfallRule.objects.create(**payload.dict())
    except IntegrityError:
        raise HttpError(400, "A rule with that description already exists")
    api_logger.info(f"Windfall rule created : {rule.rule}")
    return {"id": rule.id}


@windfall_rule_router.put("/update/{rule_id}", auth=FullAccessAuth())
def update_rule(request, rule_id: int, payload: WindfallRuleIn):
    rule = get_object_or_404(WindfallRule, id=rule_id)
    for field, value in payload.dict().items():
        setattr(rule, field, value)
    try:
        rule.save()
    except IntegrityError:
        raise HttpError(400, "A rule with that description already exists")
    return {"success": True}


@windfall_rule_router.delete("/delete/{rule_id}", auth=FullAccessAuth())
def delete_rule(request, rule_id: int):
    get_object_or_404(WindfallRule, id=rule_id).delete()
    return {"success": True}
