import logging
from decimal import Decimal

from django.db import transaction as db_transaction
from ninja import Router
from ninja.errors import HttpError

from administration.api.dependencies.auth import FullAccessAuth
from planning.api.schemas.planner import (
    PlannerApplyIn,
    PlannerApplyOut,
    PlannerApplyResultOut,
    PlannerOut,
    PlannerRowOut,
    ProjectionOut,
    ProjectionPointOut,
)
from planning.models import Contribution
from planning.services.planner import (
    analyze_account_trend,
    analyze_contribution,
    apply_maximise_goals,
    net_per_paycheck,
    paycheck_headroom,
    project_with_contribution,
    solve_for_contribution,
)

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

planner_router = Router(tags=["Planner"])


def _signed_like(magnitude: Decimal, existing: Decimal | None) -> Decimal:
    """Give `magnitude` the sign convention the reminder already uses.

    Reminder amounts carry a sign that the transaction generator copies
    *directly* into `total_amount`: transfers and expenses are stored negative,
    income positive, with a transfer's direction encoded by its source and
    destination accounts rather than by its sign. The solver works in
    magnitudes, so writing its result raw would flip a transfer positive and
    produce a transaction inconsistent with every other one in the ledger —
    which `_signed_amount` would then read as an inflow.

    Preserving the existing sign rather than hardcoding "negative" keeps this
    correct if a contribution is ever pointed at an income-shaped reminder.
    """
    magnitude = abs(magnitude)
    return -magnitude if (existing or Decimal("0")) < 0 else magnitude


def _row(contribution, months, horizon_months):
    """Build one planner row, tolerating a contribution with nothing to analyse."""
    analysis = analyze_contribution(
        contribution, months=months, horizon_months=horizon_months
    )
    current = contribution.per_paycheck or Decimal("0")
    if analysis is None:
        return PlannerRowOut(
            contribution_id=contribution.id,
            contribution=contribution.contribution,
            account_id=None,
            account_name=None,
            reminder_id=contribution.reminder_id,
            goal_type=contribution.goal_type,
            current_per_paycheck=current,
            note="Link an account to analyse this contribution.",
        )
    note = analysis["note"]
    if note is None and contribution.goal_type == Contribution.GOAL_NONE:
        note = "No goal set — counted in the totals, but nothing to suggest."
    return PlannerRowOut(
        contribution_id=contribution.id,
        contribution=contribution.contribution,
        account_id=contribution.account_id,
        account_name=contribution.account.account_name
        if contribution.account_id
        else None,
        reminder_id=contribution.reminder_id,
        goal_type=contribution.goal_type,
        current_per_paycheck=current,
        trend=analysis["trend"],
        suggestion=analysis["suggestion"],
        drift=analysis["drift"],
        note=note,
    )


@planner_router.get("/analysis", response=PlannerOut)
def planner_analysis(
    request,
    months: int = 6,
    horizon_months: int = 12,
    income_adjustment: Decimal = Decimal("0"),
):
    """Trend, goal suggestion and reminder drift for every active contribution.

    Runs synchronously. The work is a handful of indexed queries per account
    plus arithmetic, so it stays well inside a request even with many accounts.
    """
    if months < 1 or months > 60:
        raise HttpError(400, "months must be between 1 and 60")
    if horizon_months < 1 or horizon_months > 60:
        raise HttpError(400, "horizon_months must be between 1 and 60")

    try:
        contributions = (
            Contribution.objects.filter(active=True)
            .select_related("account", "reminder", "reminder__repeat")
            .order_by("id")
        )
        rows = [_row(c, months, horizon_months) for c in contributions]

        # Second pass: "maximise" rows claim whatever the other goals leave, so
        # they can only be solved once the rest are known.
        net = net_per_paycheck()
        apply_maximise_goals(
            rows, None if net is None else net + income_adjustment
        )

        current_total = Decimal("0")
        suggested_total = Decimal("0")
        for row in rows:
            current_total += row.current_per_paycheck
            # Nothing to suggest means nothing changes — the contribution still
            # costs what it costs, so it carries into the suggested total too.
            suggested_total += (
                row.suggestion.required_per_paycheck
                if row.suggestion
                else row.current_per_paycheck
            )

        api_logger.debug("Planner analysis retrieved")
        return PlannerOut(
            rows=rows,
            current_per_paycheck_total=current_total,
            suggested_per_paycheck_total=suggested_total,
            delta_per_paycheck_total=suggested_total - current_total,
            window_months=months,
            horizon_months=horizon_months,
            headroom=paycheck_headroom(
                current_total, suggested_total, income_adjustment
            ),
        )
    except Exception as e:
        api_logger.error("Planner analysis not retrieved")
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, f"Planner analysis error: {str(e)}")


@planner_router.get(
    "/projection/{contribution_id}", response=ProjectionOut
)
def planner_projection(request, contribution_id: int, months: int = 12):
    """Balance month by month under the current vs the suggested contribution."""
    if months < 1 or months > 120:
        raise HttpError(400, "months must be between 1 and 120")

    contribution = Contribution.objects.filter(pk=contribution_id).first()
    if not contribution:
        raise HttpError(404, "Contribution not found")
    if not contribution.account_id:
        raise HttpError(400, "This contribution has no account to project.")

    source_account_id = (
        contribution.reminder.reminder_source_account_id
        if contribution.reminder_id
        else None
    )
    trend = analyze_account_trend(
        contribution.account_id, source_account_id=source_account_id
    )
    if trend is None:
        raise HttpError(400, "Not enough cleared history to project this account.")

    suggestion = solve_for_contribution(contribution, trend)
    if suggestion is None:
        raise HttpError(400, "This contribution has no goal to project against.")

    points = [
        ProjectionPointOut(
            month=m, balance_now=now, balance_if_applied=applied
        )
        for m, now, applied in project_with_contribution(
            trend, suggestion, months=months
        )
    ]
    return ProjectionOut(contribution_id=contribution_id, points=points)


@planner_router.post("/apply", response=PlannerApplyOut, auth=FullAccessAuth())
def planner_apply(request, payload: PlannerApplyIn):
    """Write each suggested amount to its contribution and its linked reminder.

    Both are updated together, so the drift indicator resets rather than
    showing a permanent gap on every row you have ever accepted. A contribution
    with no linked reminder still updates its own planned figure — there is
    just nothing to reschedule.

    The whole batch is atomic: a partial apply would leave the paycheck total
    meaning nothing, which is the number the page exists to show.
    """
    if not payload.contribution_ids:
        raise HttpError(400, "No contributions were given to apply.")

    results = []
    try:
        with db_transaction.atomic():
            contributions = (
                Contribution.objects.select_for_update()
                .filter(pk__in=payload.contribution_ids)
                .select_related("account", "reminder", "reminder__repeat")
            )
            found = {c.id: c for c in contributions}

            for contribution_id in payload.contribution_ids:
                contribution = found.get(contribution_id)
                if not contribution:
                    results.append(
                        PlannerApplyResultOut(
                            contribution_id=contribution_id,
                            applied=False,
                            reason="Contribution not found.",
                        )
                    )
                    continue

                analysis = analyze_contribution(contribution)
                suggestion = analysis["suggestion"] if analysis else None
                if suggestion is None:
                    results.append(
                        PlannerApplyResultOut(
                            contribution_id=contribution_id,
                            applied=False,
                            reason="Nothing to apply — no goal, or no trend to measure.",
                        )
                    )
                    continue
                if not suggestion.achievable:
                    results.append(
                        PlannerApplyResultOut(
                            contribution_id=contribution_id,
                            applied=False,
                            reason=suggestion.warning or "Goal is not achievable.",
                        )
                    )
                    continue

                previous = contribution.per_paycheck
                contribution.per_paycheck = suggestion.required_per_paycheck
                contribution.save(update_fields=["per_paycheck"])

                if contribution.reminder_id:
                    reminder = contribution.reminder
                    reminder.amount = _signed_like(
                        suggestion.required_per_paycheck, reminder.amount
                    )
                    reminder.save(update_fields=["amount"])

                results.append(
                    PlannerApplyResultOut(
                        contribution_id=contribution_id,
                        applied=True,
                        previous_per_paycheck=previous,
                        new_per_paycheck=suggestion.required_per_paycheck,
                    )
                )

        applied_count = sum(1 for r in results if r.applied)
        api_logger.info(f"Planner applied {applied_count} contribution(s)")
        return PlannerApplyOut(results=results, applied_count=applied_count)
    except HttpError:
        raise
    except Exception as e:
        api_logger.error("Planner apply failed")
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, f"Planner apply error: {str(e)}")
