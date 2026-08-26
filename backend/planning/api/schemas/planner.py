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
    horizon_months: int
    observed_slope_per_month: AmountDecimal
    r_squared: float
    data_points: int
    window_months: int
    current_balance: AmountDecimal
    excluded_contribution_total: AmountDecimal
    one_off_total: AmountDecimal

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
    trend: Optional[TrendOut] = None
    suggestion: Optional[SuggestionOut] = None
    # None means no reminder is linked, which is not the same as zero drift.
    drift: Optional[AmountDecimal] = None
    note: Optional[str] = None


class HeadroomOut(Schema):
    """Whether the plan actually fits in a pay period."""

    net_per_paycheck: Optional[AmountDecimal] = None
    income_adjustment: AmountDecimal
    headroom_now: Optional[AmountDecimal] = None
    headroom_if_applied: Optional[AmountDecimal] = None
    affordable: Optional[bool] = None
    note: Optional[str] = None


class PlannerOut(Schema):
    """The whole planner view, with paycheck totals for the summary row."""

    rows: List[PlannerRowOut]
    current_per_paycheck_total: AmountDecimal
    suggested_per_paycheck_total: AmountDecimal
    delta_per_paycheck_total: AmountDecimal
    window_months: int
    horizon_months: int
    headroom: HeadroomOut


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
    """Which contributions to apply the suggested amount to."""

    contribution_ids: List[int]


class PlannerApplyResultOut(Schema):
    contribution_id: int
    applied: bool
    previous_per_paycheck: Optional[AmountDecimal] = None
    new_per_paycheck: Optional[AmountDecimal] = None
    reason: Optional[str] = None


class PlannerApplyOut(Schema):
    results: List[PlannerApplyResultOut]
    applied_count: int
