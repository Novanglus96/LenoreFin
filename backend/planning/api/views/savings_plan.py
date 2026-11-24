"""HTTP for the savings plan: view, simulate edits, accept, windfalls."""

import logging
from datetime import date
from decimal import Decimal
from typing import Any, List, Optional

from django.shortcuts import get_object_or_404

from ninja import Router, Schema
from ninja.errors import HttpError

from administration.api.dependencies.auth import FullAccessAuth
from planning.models import PlanAcceptance, WindfallApplication
from planning.services import windfall
from planning.services.accept import PlanError, accept_plan, revert_acceptance
from planning.services.savings_plan import build_plan
from utils.dates import get_todays_date_timezone_adjusted

api_logger = logging.getLogger("api")

savings_plan_router = Router(tags=["Savings Plan"])


class PlanRequest(Schema):
    start: Optional[date] = None
    end: Optional[date] = None
    edits: Optional[dict[str, Any]] = None
    # Accept an insolvent plan anyway. Ignored when simulating.
    force: bool = False


def _plan(payload: PlanRequest) -> dict:
    plan = build_plan(
        get_todays_date_timezone_adjusted(), payload.start, payload.end, payload.edits
    )
    if "error" in plan:
        raise HttpError(400, plan["error"])
    return plan


@savings_plan_router.get("/")
def get_plan(request, start: Optional[date] = None, end: Optional[date] = None):
    return _plan(PlanRequest(start=start, end=end))


@savings_plan_router.post("/simulate")
def simulate_plan(request, payload: PlanRequest):
    """Re-run the plan with the page's edits. Arithmetic only once warmed."""
    return _plan(payload)


# --------------------------------------------------------------------------
# Accepting


def _acceptance_out(a) -> dict:
    return {
        "id": a.id,
        "accepted_on": a.accepted_on,
        "window_start": a.window_start,
        "window_end": a.window_end,
        "total_per_paycheck": a.total_per_paycheck,
        "verdict": a.verdict,
        "reverted_on": a.reverted_on,
        "imported": a.imported,
        "buckets": [
            {
                "bucket_name": b.bucket_name,
                "action": b.action,
                "per_paycheck": b.per_paycheck,
                "previous_per_paycheck": b.previous_per_paycheck,
            }
            for b in a.buckets.all()
        ],
    }


@savings_plan_router.post("/accept", auth=FullAccessAuth())
def accept(request, payload: PlanRequest):
    try:
        acceptance = accept_plan(
            get_todays_date_timezone_adjusted(),
            payload.start,
            payload.end,
            payload.edits,
            force=payload.force,
        )
    except PlanError as e:
        raise HttpError(400, str(e))
    api_logger.info(f"Savings plan accepted : #{acceptance.id}")
    return _acceptance_out(acceptance)


@savings_plan_router.get("/acceptances")
def acceptances(request):
    return [_acceptance_out(a) for a in PlanAcceptance.objects.all()[:20]]


@savings_plan_router.post("/acceptances/{acceptance_id}/revert", auth=FullAccessAuth())
def revert(request, acceptance_id: int):
    acceptance = get_object_or_404(PlanAcceptance, id=acceptance_id)
    try:
        revert_acceptance(acceptance, get_todays_date_timezone_adjusted())
    except PlanError as e:
        raise HttpError(400, str(e))
    api_logger.info(f"Savings plan reverted : #{acceptance_id}")
    return _acceptance_out(acceptance)


# --------------------------------------------------------------------------
# Windfalls


class WindfallSuggestIn(Schema):
    amount: Decimal


class WindfallShareIn(Schema):
    bucket_id: int
    amount: Decimal
    suggested: Optional[Decimal] = None


class WindfallApplyIn(Schema):
    amount: Decimal
    arrival_date: date
    source_account_id: int
    allocations: List[WindfallShareIn]
    memo: Optional[str] = None


def _windfall_out(w) -> dict:
    return {
        "id": w.id,
        "applied_on": w.applied_on,
        "arrival_date": w.arrival_date,
        "amount": w.amount,
        "allocated": w.allocated,
        "source_account_id": w.source_account_id,
        "reverted_on": w.reverted_on,
        "allocations": [
            {"bucket_name": a.bucket_name, "amount": a.amount, "suggested": a.suggested}
            for a in w.allocations.all()
        ],
    }


@savings_plan_router.post("/windfall/suggest")
def windfall_suggest(request, payload: WindfallSuggestIn):
    if payload.amount <= 0:
        raise HttpError(400, "A windfall must be more than zero")
    return windfall.suggest(payload.amount, get_todays_date_timezone_adjusted())


@savings_plan_router.post("/windfall/apply", auth=FullAccessAuth())
def windfall_apply(request, payload: WindfallApplyIn):
    try:
        application = windfall.apply(
            payload.amount,
            payload.arrival_date,
            payload.source_account_id,
            [a.dict() for a in payload.allocations],
            get_todays_date_timezone_adjusted(),
            payload.memo,
        )
    except windfall.WindfallError as e:
        raise HttpError(400, str(e))
    api_logger.info(f"Windfall applied : #{application.id}")
    return _windfall_out(application)


@savings_plan_router.get("/windfalls")
def windfalls(request):
    return [_windfall_out(w) for w in WindfallApplication.objects.all()[:20]]


@savings_plan_router.post("/windfalls/{application_id}/revert", auth=FullAccessAuth())
def windfall_revert(request, application_id: int):
    application = get_object_or_404(WindfallApplication, id=application_id)
    try:
        windfall.revert(application, get_todays_date_timezone_adjusted())
    except windfall.WindfallError as e:
        raise HttpError(400, str(e))
    return _windfall_out(application)
