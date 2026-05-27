from ninja import Router
from ninja.errors import HttpError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from typing import List, Optional
from datetime import timedelta
import logging

from dateutil.relativedelta import relativedelta

from reports.models import ReportConfig, ReportConfigTag, ReportResult
from reports.api.schemas.report import (
    ReportConfigIn,
    ReportConfigOut,
    ReportResultOut,
    ReportResultRecordOut,
    ReportRunIn,
)
from reports.services.execution import run_report

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

report_router = Router(tags=["Reports"])


def _compute_next_run(frequency: str, schedule_day: Optional[int]):
    now = timezone.now()
    day = max(1, min(28, schedule_day or 1))
    if frequency == "DAILY":
        return (now + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
    if frequency == "WEEKLY":
        # schedule_day: 0=Mon … 6=Sun
        target_weekday = max(0, min(6, schedule_day or 0))
        days_ahead = target_weekday - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return (now + timedelta(days=days_ahead)).replace(hour=6, minute=0, second=0, microsecond=0)
    if frequency == "MONTHLY":
        this_month_target = now.replace(day=day, hour=6, minute=0, second=0, microsecond=0)
        if this_month_target > now:
            return this_month_target
        return (now.replace(day=1) + relativedelta(months=1)).replace(
            day=day, hour=6, minute=0, second=0, microsecond=0
        )
    return None


def _serialize_config(config: ReportConfig, requesting_user=None) -> dict:
    is_owner = (
        requesting_user is not None
        and config.created_by_id is not None
        and config.created_by_id == requesting_user.pk
    )
    return {
        "id": config.id,
        "name": config.name,
        "description": config.description,
        "report_type": config.report_type,
        "date_range_type": config.date_range_type,
        "date_from": config.date_from,
        "date_to": config.date_to,
        "period2_date_from": config.period2_date_from,
        "period2_date_to": config.period2_date_to,
        "account_ids": list(config.accounts.values_list("id", flat=True)),
        "group_by": config.group_by,
        "show_transactions": config.show_transactions,
        "show_subtotal": config.show_subtotal,
        "include_pending": config.include_pending,
        "is_shared": config.is_shared,
        "is_owner": is_owner,
        "is_scheduled": config.is_scheduled,
        "schedule_frequency": config.schedule_frequency,
        "schedule_day": config.schedule_day,
        "next_run_at": config.next_run_at,
        "tag_selections": [
            {
                "id": sel.id,
                "tag_id": sel.tag_id,
                "sub_tag_id": sel.sub_tag_id,
                "main_tag_id": sel.main_tag_id,
            }
            for sel in config.tag_selections.all()
        ],
        "created_at": config.created_at,
        "updated_at": config.updated_at,
    }


def _apply_tag_selections(config: ReportConfig, selections: list):
    config.tag_selections.all().delete()
    for sel in selections:
        tag_id = sel.tag_id
        sub_tag_id = sel.sub_tag_id
        main_tag_id = sel.main_tag_id
        filled = sum([tag_id is not None, sub_tag_id is not None, main_tag_id is not None])
        if filled != 1:
            raise HttpError(400, "Each tag selection must set exactly one of tag_id, sub_tag_id, or main_tag_id.")
        ReportConfigTag.objects.create(
            report=config,
            tag_id=tag_id,
            sub_tag_id=sub_tag_id,
            main_tag_id=main_tag_id,
        )


def _can_modify(config: ReportConfig, user) -> bool:
    is_owner = config.created_by_id is not None and config.created_by_id == user.pk
    is_full_access = user.groups.filter(name="Full Access").exists()
    return is_owner or is_full_access


def _run_from_params(
    report_type, date_range_type, group_by, date_from, date_to,
    account_ids, tag_selections_raw, show_transactions, show_subtotal, include_pending,
    period2_date_from=None, period2_date_to=None,
):
    valid_types = {"TOTALS", "COMPARISON"}
    valid_ranges = {"THIS_YEAR", "LAST_YEAR", "THIS_QUARTER", "LAST_QUARTER", "TRAILING_12", "CUSTOM"}
    valid_groups = {"TAG", "MONTH"}

    if report_type not in valid_types:
        raise HttpError(400, f"Invalid report_type. Choose from: {', '.join(valid_types)}")
    if date_range_type not in valid_ranges:
        raise HttpError(400, f"Invalid date_range_type. Choose from: {', '.join(valid_ranges)}")
    if group_by not in valid_groups:
        raise HttpError(400, f"Invalid group_by. Choose from: {', '.join(valid_groups)}")
    if date_range_type == "CUSTOM" and (not date_from or not date_to):
        raise HttpError(400, "date_from and date_to are required when date_range_type is CUSTOM.")

    tag_dicts = [
        {"tag_id": s.tag_id, "sub_tag_id": s.sub_tag_id, "main_tag_id": s.main_tag_id}
        for s in tag_selections_raw
    ]

    return run_report(
        report_type=report_type,
        date_range_type=date_range_type,
        group_by=group_by,
        date_from=date_from,
        date_to=date_to,
        account_ids=account_ids,
        tag_selections=tag_dicts,
        show_transactions=show_transactions,
        show_subtotal=show_subtotal,
        include_pending=include_pending,
        period2_date_from=period2_date_from,
        period2_date_to=period2_date_to,
    )


def _safe_user(request):
    """Return request.user only if it's a real persisted User (integer PK).
    Falls back to None for AnonymousUser, Mock objects, and bare requests."""
    try:
        user = request.user
        return user if isinstance(getattr(user, "pk", None), int) else None
    except AttributeError:
        return None


# ---------------------------------------------------------------------------
# Literal routes must be declared BEFORE parametric routes so Django URL
# matching hits them first (Django matches patterns in registration order).
# ---------------------------------------------------------------------------

@report_router.get("", response=List[ReportConfigOut])
def list_reports(request):
    user = request.user
    configs = ReportConfig.objects.prefetch_related("tag_selections", "accounts").filter(
        Q(created_by=user) | Q(is_shared=True)
    )
    return [_serialize_config(c, user) for c in configs]


@report_router.post("", response=ReportConfigOut)
def create_report(request, payload: ReportConfigIn):
    try:
        next_run = (
            _compute_next_run(payload.schedule_frequency, payload.schedule_day)
            if payload.is_scheduled and payload.schedule_frequency
            else None
        )
        config = ReportConfig.objects.create(
            name=payload.name,
            description=payload.description,
            report_type=payload.report_type,
            date_range_type=payload.date_range_type,
            date_from=payload.date_from,
            date_to=payload.date_to,
            period2_date_from=payload.period2_date_from,
            period2_date_to=payload.period2_date_to,
            group_by=payload.group_by,
            show_transactions=payload.show_transactions,
            show_subtotal=payload.show_subtotal,
            include_pending=payload.include_pending,
            is_shared=payload.is_shared,
            is_scheduled=payload.is_scheduled,
            schedule_frequency=payload.schedule_frequency if payload.is_scheduled else None,
            schedule_day=payload.schedule_day if payload.is_scheduled else None,
            next_run_at=next_run,
            created_by=_safe_user(request),
        )
        if payload.account_ids:
            config.accounts.set(payload.account_ids)
        _apply_tag_selections(config, payload.tag_selections)
        api_logger.info(f"Report config created: {config.name}")
        return _serialize_config(config, request.user)
    except HttpError:
        raise
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, "Failed to create report config")


@report_router.post("/run", response=ReportResultOut)
def run_adhoc_report(request, payload: ReportRunIn):
    try:
        result = _run_from_params(
            report_type=payload.report_type,
            date_range_type=payload.date_range_type,
            group_by=payload.group_by,
            date_from=payload.date_from,
            date_to=payload.date_to,
            account_ids=payload.account_ids,
            tag_selections_raw=payload.tag_selections,
            show_transactions=payload.show_transactions,
            show_subtotal=payload.show_subtotal,
            include_pending=payload.include_pending,
            period2_date_from=payload.period2_date_from,
            period2_date_to=payload.period2_date_to,
        )
        return result
    except HttpError:
        raise
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, "Failed to run report")


@report_router.get("/{report_id}", response=ReportConfigOut)
def get_report(request, report_id: int):
    user = request.user
    config = get_object_or_404(
        ReportConfig.objects.prefetch_related("tag_selections", "accounts"),
        id=report_id,
    )
    if not (config.created_by_id == user.pk or config.is_shared):
        raise HttpError(404, "Report not found")
    return _serialize_config(config, user)


@report_router.put("/{report_id}", response=ReportConfigOut)
def update_report(request, report_id: int, payload: ReportConfigIn):
    try:
        config = get_object_or_404(ReportConfig, id=report_id)
        if not _can_modify(config, request.user):
            raise HttpError(403, "You do not have permission to modify this report")
        next_run = (
            _compute_next_run(payload.schedule_frequency, payload.schedule_day)
            if payload.is_scheduled and payload.schedule_frequency
            else None
        )
        config.name = payload.name
        config.description = payload.description
        config.report_type = payload.report_type
        config.date_range_type = payload.date_range_type
        config.date_from = payload.date_from
        config.date_to = payload.date_to
        config.period2_date_from = payload.period2_date_from
        config.period2_date_to = payload.period2_date_to
        config.group_by = payload.group_by
        config.show_transactions = payload.show_transactions
        config.show_subtotal = payload.show_subtotal
        config.include_pending = payload.include_pending
        config.is_shared = payload.is_shared
        config.is_scheduled = payload.is_scheduled
        config.schedule_frequency = payload.schedule_frequency if payload.is_scheduled else None
        config.schedule_day = payload.schedule_day if payload.is_scheduled else None
        config.next_run_at = next_run
        config.save()
        config.accounts.set(payload.account_ids)
        _apply_tag_selections(config, payload.tag_selections)
        api_logger.info(f"Report config updated: {config.name}")
        return _serialize_config(config, request.user)
    except (HttpError, Http404):
        raise
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, "Failed to update report config")


@report_router.delete("/{report_id}")
def delete_report(request, report_id: int):
    try:
        config = get_object_or_404(ReportConfig, id=report_id)
        if not _can_modify(config, request.user):
            raise HttpError(403, "You do not have permission to delete this report")
        name = config.name
        config.delete()
        api_logger.info(f"Report config deleted: {name}")
        return {"success": True}
    except (HttpError, Http404):
        raise
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, "Failed to delete report config")


@report_router.post("/{report_id}/run", response=ReportResultOut)
def run_saved_report(request, report_id: int):
    try:
        user = request.user
        config = get_object_or_404(
            ReportConfig.objects.prefetch_related("tag_selections", "accounts"),
            id=report_id,
        )
        if not (config.created_by_id == user.pk or config.is_shared):
            raise HttpError(404, "Report not found")
        tag_selections_raw = list(config.tag_selections.all())
        result = _run_from_params(
            report_type=config.report_type,
            date_range_type=config.date_range_type,
            group_by=config.group_by,
            date_from=config.date_from,
            date_to=config.date_to,
            account_ids=list(config.accounts.values_list("id", flat=True)),
            tag_selections_raw=tag_selections_raw,
            show_transactions=config.show_transactions,
            show_subtotal=config.show_subtotal,
            include_pending=config.include_pending,
            period2_date_from=config.period2_date_from,
            period2_date_to=config.period2_date_to,
        )
        return result
    except (HttpError, Http404):
        raise
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, "Failed to run saved report")


@report_router.get("/{report_id}/results", response=List[ReportResultRecordOut])
def list_report_results(request, report_id: int):
    user = request.user
    config = get_object_or_404(ReportConfig, id=report_id)
    if not (config.created_by_id == user.pk or config.is_shared):
        raise HttpError(404, "Report not found")
    results = ReportResult.objects.filter(config=config).only(
        "id", "run_at", "status", "error_message"
    )[:20]
    return [
        {
            "id": r.id,
            "run_at": r.run_at,
            "status": r.status,
            "error_message": r.error_message,
            "result_data": None,
        }
        for r in results
    ]


@report_router.get("/{report_id}/results/{result_id}", response=ReportResultRecordOut)
def get_report_result(request, report_id: int, result_id: int):
    user = request.user
    config = get_object_or_404(ReportConfig, id=report_id)
    if not (config.created_by_id == user.pk or config.is_shared):
        raise HttpError(404, "Report not found")
    result = get_object_or_404(ReportResult, id=result_id, config=config)
    return {
        "id": result.id,
        "run_at": result.run_at,
        "status": result.status,
        "error_message": result.error_message,
        "result_data": result.result_data,
    }
