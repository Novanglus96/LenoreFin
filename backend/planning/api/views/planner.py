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
    allocate_capacity,
    minimum_per_paycheck,
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
            topup_per_paycheck=Decimal("0.00"),
            effective_per_paycheck=current,
            minimum_per_paycheck=Decimal("0.00"),
            allocated_per_paycheck=current,
            move_per_paycheck=Decimal("0.00"),
            note="Link an account to analyse this contribution.",
        )
    note = analysis["note"]
    if note is None and contribution.goal_type == Contribution.GOAL_NONE:
        note = "No goal set — counted in the totals, but nothing to suggest."
    trend = analysis["trend"]
    # Top-ups are funding that is already happening, so the row's baseline is
    # the scheduled transfer plus them. Comparing a suggestion against the
    # scheduled figure alone counts money that is already going in as money that
    # still needs finding.
    topup = trend.topup_per_paycheck if trend else Decimal("0.00")
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
        topup_per_paycheck=topup,
        effective_per_paycheck=(current + topup).quantize(Decimal("0.01")),
        minimum_per_paycheck=minimum_per_paycheck(trend),
        # Filled in by `allocate_capacity`, which needs every row before it can
        # decide any of them.
        allocated_per_paycheck=current,
        move_per_paycheck=Decimal("0.00"),
        trend=trend,
        suggestion=analysis["suggestion"],
        drift=analysis["drift"],
        note=note,
    )


def _build_analysis(months, horizon_months, income_adjustment):
    """Every row, plus the one allocation they were decided by.

    Shared by the read and the apply so the two cannot disagree. Applying is
    the only place the numbers actually get written, and a contribution's share
    depends on every *other* contribution — so recomputing it per-row on the way
    in would write figures the page never showed.
    """
    contributions = (
        Contribution.objects.filter(active=True)
        .select_related("account", "reminder", "reminder__repeat")
        .order_by("id")
    )
    rows = [_row(c, months, horizon_months) for c in contributions]

    current_total = Decimal("0")
    effective_total = Decimal("0")
    suggested_total = Decimal("0")
    for row in rows:
        current_total += row.current_per_paycheck
        effective_total += row.effective_per_paycheck
        # Nothing to suggest means nothing changes — the contribution still
        # costs what it costs, so it carries into the suggested total too.
        suggested_total += (
            row.suggestion.required_per_paycheck
            if row.suggestion
            else row.current_per_paycheck
        )

    # Capacity is measured against what is *effectively* being allocated —
    # scheduled transfers plus the top-ups being made by hand — because that is
    # what the household has demonstrably been sustaining.
    headroom = paycheck_headroom(
        effective_total,
        suggested_total,
        income_adjustment,
        months=months,
        horizon_months=horizon_months,
    )
    # One constrained distribution, not N independent solves. This also resolves
    # the "maximise" rows, which can only be answered once everything else has
    # taken its share.
    allocation = allocate_capacity(rows, headroom["allocatable_per_paycheck"])
    # Maximise rows changed inside the allocation, so a total built before it is
    # stale.
    suggested_total = sum(
        (
            r.suggestion.required_per_paycheck
            if r.suggestion
            else r.current_per_paycheck
        )
        for r in rows
    )
    return {
        "rows": rows,
        "current_total": current_total,
        "effective_total": effective_total,
        "suggested_total": suggested_total,
        "headroom": headroom,
        "allocation": allocation,
    }


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
        built = _build_analysis(months, horizon_months, income_adjustment)
        api_logger.debug("Planner analysis retrieved")
        return PlannerOut(
            rows=built["rows"],
            current_per_paycheck_total=built["current_total"],
            effective_per_paycheck_total=built["effective_total"],
            suggested_per_paycheck_total=built["suggested_total"],
            delta_per_paycheck_total=(
                built["suggested_total"] - built["current_total"]
            ),
            window_months=months,
            horizon_months=horizon_months,
            headroom=built["headroom"],
            allocation=built["allocation"],
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

            # The allocation is the thing being applied, and a contribution's
            # share depends on every other one — so it is computed once, over
            # the whole set, exactly as the page computed it. Solving each row
            # again on its own would write figures that were never displayed,
            # and would hand every "maximise" row a residual calculated against
            # a different plan.
            built = _build_analysis(
                payload.months,
                payload.horizon_months,
                payload.income_adjustment,
            )
            allocated = {r.contribution_id: r for r in built["rows"]}

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

                row = allocated.get(contribution_id)
                suggestion = row.suggestion if row else None
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

                # What the allocation granted, not what the goal asked for.
                # When the pot cannot stretch to every goal these differ, and
                # the granted figure is the one that fits.
                amount = row.allocated_per_paycheck
                previous = contribution.per_paycheck
                contribution.per_paycheck = amount
                contribution.save(update_fields=["per_paycheck"])

                if contribution.reminder_id:
                    reminder = contribution.reminder
                    reminder.amount = _signed_like(amount, reminder.amount)
                    reminder.save(update_fields=["amount"])

                results.append(
                    PlannerApplyResultOut(
                        contribution_id=contribution_id,
                        applied=True,
                        previous_per_paycheck=previous,
                        new_per_paycheck=amount,
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
