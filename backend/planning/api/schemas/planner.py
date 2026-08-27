from datetime import date
from decimal import Decimal
from ninja import Schema
from typing import List, Optional
from pydantic import ConfigDict, condecimal

AmountDecimal = condecimal(max_digits=12, decimal_places=2)


class TrendOut(Schema):
    """What an account does on its own, with contributions excluded."""

    natural_flow_per_month: AmountDecimal
    # What the solver actually uses: forward scheduled flow plus ad-hoc spend.
    scheduled_flow_per_month: AmountDecimal
    adhoc_flow_per_month: AmountDecimal
    projected_flow_per_month: AmountDecimal
    paychecks_per_year: condecimal(max_digits=8, decimal_places=4)
    paychecks_in_horizon: condecimal(max_digits=8, decimal_places=2)
    scheduled_flow_per_paycheck: AmountDecimal
    adhoc_flow_per_paycheck: AmountDecimal
    projected_flow_per_paycheck: AmountDecimal
    horizon_months: int
    observed_slope_per_month: AmountDecimal
    r_squared: float
    data_points: int
    window_months: int
    current_balance: AmountDecimal
    excluded_contribution_total: AmountDecimal
    one_off_total: AmountDecimal
    extra_contributions_total: AmountDecimal
    topup_per_paycheck: AmountDecimal
    modal_contribution_amount: Optional[AmountDecimal] = None
    projected_low_balance: AmountDecimal
    paychecks_to_low: condecimal(max_digits=8, decimal_places=2)
    suggested_floor: AmountDecimal

    model_config = ConfigDict(from_attributes=True)


class SuggestionOut(Schema):
    """A per-paycheck figure and everything needed to judge it."""

    goal_type: str
    current_per_paycheck: AmountDecimal
    required_per_paycheck: AmountDecimal
    delta_per_paycheck: AmountDecimal
    paychecks_per_year: condecimal(max_digits=8, decimal_places=4)
    reason: str
    achievable: bool
    warning: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PlannerRowOut(Schema):
    """One contribution's full picture, as the planner table renders it."""

    contribution_id: int
    contribution: str
    account_id: Optional[int] = None
    account_name: Optional[str] = None
    reminder_id: Optional[int] = None
    goal_type: str
    # What is being contributed today. Lives on the row rather than only inside
    # `suggestion`, because a contribution with no goal has no suggestion but is
    # still costing money every payday.
    current_per_paycheck: AmountDecimal
    # Hand top-ups expressed as a rate, and the baseline they add up to. The
    # effective figure is what the allocation compares against — the scheduled
    # amount alone treats money already going in as money still to be found.
    topup_per_paycheck: AmountDecimal
    effective_per_paycheck: AmountDecimal
    # The dated, unavoidable share of this bucket. Zero for one whose spending
    # is entirely ad-hoc, which means "nothing fixed", not "nothing needed".
    minimum_per_paycheck: AmountDecimal
    # What the constrained allocation actually gives this row, and how far that
    # is from what it effectively gets today. The move is the actionable number.
    allocated_per_paycheck: AmountDecimal
    move_per_paycheck: AmountDecimal
    trend: Optional[TrendOut] = None
    suggestion: Optional[SuggestionOut] = None
    # None means no reminder is linked, which is not the same as zero drift.
    drift: Optional[AmountDecimal] = None
    note: Optional[str] = None


class ReminderChangeOut(Schema):
    """A commitment that starts or stops inside the horizon."""

    reminder_id: int
    description: str
    change_per_year: AmountDecimal
    starts: Optional[date] = None
    ends: Optional[date] = None


class HeadroomOut(Schema):
    """Whether the plan actually fits in a pay period."""

    # Take-home, for context only — it is NOT the capacity figure.
    net_per_paycheck: Optional[AmountDecimal] = None
    # What can actually be allocated: today's allocation plus the funding
    # account's drift, plus any stated income change.
    allocatable_per_paycheck: Optional[AmountDecimal] = None
    funding_account_drift: Optional[AmountDecimal] = None
    # How capacity shifts over the horizon as reminders start and end — the one
    # part measured drift cannot see.
    forward_reminder_change: Optional[AmountDecimal] = None
    reminder_changes: List[ReminderChangeOut] = []
    income_adjustment: AmountDecimal
    headroom_now: Optional[AmountDecimal] = None
    headroom_if_applied: Optional[AmountDecimal] = None
    affordable: Optional[bool] = None
    note: Optional[str] = None


class MoveOut(Schema):
    """Take this much off one contribution and put it on another."""

    from_contribution_id: int
    from_contribution: str
    to_contribution_id: int
    to_contribution: str
    amount_per_paycheck: AmountDecimal


class AllocationOut(Schema):
    """The result of distributing one pot, rather than summing wishes."""

    capacity_per_paycheck: Optional[AmountDecimal] = None
    obligations_total: AmountDecimal
    desired_total: AmountDecimal
    allocated_total: AmountDecimal
    effective_total: AmountDecimal
    # Capacity left when there is no `maximise` bucket to absorb it.
    unallocated: AmountDecimal
    # How much the plan shrinks or grows overall. The paired moves cannot show
    # this — they only match a giver to a taker.
    net_change_total: AmountDecimal
    # False when dated obligations alone overrun capacity — the one case moving
    # money between buckets cannot fix.
    feasible: Optional[bool] = None
    shortfall: Optional[AmountDecimal] = None
    moves: List[MoveOut] = []
    note: Optional[str] = None


class PlannerOut(Schema):
    """The whole planner view, with paycheck totals for the summary row."""

    rows: List[PlannerRowOut]
    current_per_paycheck_total: AmountDecimal
    # Scheduled plus top-ups: what is really being put aside each payday.
    effective_per_paycheck_total: AmountDecimal
    suggested_per_paycheck_total: AmountDecimal
    delta_per_paycheck_total: AmountDecimal
    window_months: int
    horizon_months: int
    headroom: HeadroomOut
    allocation: AllocationOut


class ProjectionPointOut(Schema):
    month: int
    balance_now: AmountDecimal
    balance_if_applied: AmountDecimal


class ProjectionOut(Schema):
    contribution_id: int
    points: List[ProjectionPointOut]
    # Superimposed on the measured trend rather than compounded, so an
    # interest-bearing account is under-estimated. Surfaced, not hidden.
    approximate: bool = True


class PlannerApplyIn(Schema):
    """Which contributions to apply, and the view they were decided under.

    The window and horizon come along because the allocation depends on them:
    applying under different settings than the page displayed would write
    figures the user never saw.
    """

    contribution_ids: List[int]
    months: int = 6
    horizon_months: int = 12
    income_adjustment: AmountDecimal = Decimal("0")


class PlannerApplyResultOut(Schema):
    contribution_id: int
    applied: bool
    previous_per_paycheck: Optional[AmountDecimal] = None
    new_per_paycheck: Optional[AmountDecimal] = None
    reason: Optional[str] = None


class PlannerApplyOut(Schema):
    results: List[PlannerApplyResultOut]
    applied_count: int
