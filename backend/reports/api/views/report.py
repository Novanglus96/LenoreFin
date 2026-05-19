from ninja import Router
from ninja.errors import HttpError
from django.http import Http404
from django.shortcuts import get_object_or_404
from typing import List
import logging

from administration.api.dependencies.auth import FullAccessAuth
from reports.models import ReportConfig, ReportConfigTag
from reports.api.schemas.report import (
    ReportConfigIn,
    ReportConfigOut,
    ReportResultOut,
    ReportRunIn,
)
from reports.services.execution import run_report

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

report_router = Router(tags=["Reports"])


def _serialize_config(config: ReportConfig) -> dict:
    return {
        "id": config.id,
        "name": config.name,
        "description": config.description,
        "report_type": config.report_type,
        "date_range_type": config.date_range_type,
        "date_from": config.date_from,
        "date_to": config.date_to,
        "account_ids": list(config.accounts.values_list("id", flat=True)),
        "group_by": config.group_by,
        "show_transactions": config.show_transactions,
        "show_subtotal": config.show_subtotal,
        "include_pending": config.include_pending,
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


def _run_from_params(
    report_type, date_range_type, group_by, date_from, date_to,
    account_ids, tag_selections_raw, show_transactions, show_subtotal, include_pending
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
    configs = ReportConfig.objects.prefetch_related("tag_selections", "accounts").all()
    return [_serialize_config(c) for c in configs]


@report_router.post("", response=ReportConfigOut, auth=FullAccessAuth())
def create_report(request, payload: ReportConfigIn):
    try:
        config = ReportConfig.objects.create(
            name=payload.name,
            description=payload.description,
            report_type=payload.report_type,
            date_range_type=payload.date_range_type,
            date_from=payload.date_from,
            date_to=payload.date_to,
            group_by=payload.group_by,
            show_transactions=payload.show_transactions,
            show_subtotal=payload.show_subtotal,
            include_pending=payload.include_pending,
            created_by=_safe_user(request),
        )
        if payload.account_ids:
            config.accounts.set(payload.account_ids)
        _apply_tag_selections(config, payload.tag_selections)
        api_logger.info(f"Report config created: {config.name}")
        return _serialize_config(config)
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
        )
        return result
    except HttpError:
        raise
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, "Failed to run report")


@report_router.get("/{report_id}", response=ReportConfigOut)
def get_report(request, report_id: int):
    config = get_object_or_404(
        ReportConfig.objects.prefetch_related("tag_selections", "accounts"),
        id=report_id,
    )
    return _serialize_config(config)


@report_router.put("/{report_id}", response=ReportConfigOut, auth=FullAccessAuth())
def update_report(request, report_id: int, payload: ReportConfigIn):
    try:
        config = get_object_or_404(ReportConfig, id=report_id)
        config.name = payload.name
        config.description = payload.description
        config.report_type = payload.report_type
        config.date_range_type = payload.date_range_type
        config.date_from = payload.date_from
        config.date_to = payload.date_to
        config.group_by = payload.group_by
        config.show_transactions = payload.show_transactions
        config.show_subtotal = payload.show_subtotal
        config.include_pending = payload.include_pending
        config.save()
        config.accounts.set(payload.account_ids)
        _apply_tag_selections(config, payload.tag_selections)
        api_logger.info(f"Report config updated: {config.name}")
        return _serialize_config(config)
    except (HttpError, Http404):
        raise
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, "Failed to update report config")


@report_router.delete("/{report_id}", auth=FullAccessAuth())
def delete_report(request, report_id: int):
    try:
        config = get_object_or_404(ReportConfig, id=report_id)
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
        config = get_object_or_404(
            ReportConfig.objects.prefetch_related("tag_selections", "accounts"),
            id=report_id,
        )
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
        )
        return result
    except (HttpError, Http404):
        raise
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, "Failed to run saved report")
