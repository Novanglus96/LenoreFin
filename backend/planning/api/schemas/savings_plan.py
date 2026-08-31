from datetime import date
from typing import List, Optional

from ninja import Schema
from pydantic import ConfigDict, condecimal

AmountDecimal = condecimal(max_digits=12, decimal_places=2)


# The class PlanLineOut is a schema for one bucket's share of the plan.
class PlanLineOut(Schema):
    bucket_id: int
    bucket_name: str
    account_id: Optional[int] = None
    account_name: Optional[str] = None
    priority: int
    sweep: bool
    sweep_share: int
    lendable: bool
    receives_rewards: bool

    current_per_paycheck: AmountDecimal
    minimum_per_paycheck: AmountDecimal
    # False when the minimum was derived from the account's own budgets and
    # bills rather than stated by the user, which is worth showing: one is a
    # decision and the other is a consequence.
    minimum_is_stated: bool
    target_per_paycheck: AmountDecimal
    planned_per_paycheck: AmountDecimal
    # Positive means this account is being given more than it needs.
    freed_per_paycheck: AmountDecimal
    optional_per_paycheck: AmountDecimal

    budgeted_per_paycheck: AmountDecimal
    budget_names: List[str] = []
    # Card rewards expected to land here, and when.
    rewards_expected: AmountDecimal
    rewards_on: Optional[date] = None
    # Spending measured from linked tags because no budget describes it.
    measured_per_year: AmountDecimal
    measured_tag_names: List[str] = []
    target_balance: Optional[AmountDecimal] = None
    projected_low: AmountDecimal
    projected_low_date: Optional[date] = None
    observed_spend_per_month: AmountDecimal
    spend_variance_per_paycheck: AmountDecimal
    reason: str
    warning: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# The class DipOut is a schema for one run below an account's floor.
class DipOut(Schema):
    account: str
    account_name: Optional[str] = None
    # `one_off` is a transfer to schedule; `structural` means the plan is wrong.
    kind: str
    when: date
    low_when: date
    balance: AmountDecimal
    floor: AmountDecimal
    one_off_needed: AmountDecimal
    recovers_on: Optional[date] = None
    days_below: int
    paydays_below: int
    why: str


# The class BridgeMovementOut is a schema for one leg of a bridging transfer.
class BridgeMovementOut(Schema):
    from_account_id: Optional[int] = None
    from_account: Optional[str] = None
    bucket_name: str
    amount: AmountDecimal
    annual_rate: AmountDecimal
    # What that account could have spared in total, so the user can see how
    # much room the movement leaves behind it.
    spare: AmountDecimal


# The class BridgeOut is a schema for one dated bridging transfer.
class BridgeOut(Schema):
    for_account_id: Optional[int] = None
    when: date
    return_on: Optional[date] = None
    amount: AmountDecimal
    covered: AmountDecimal
    shortfall: AmountDecimal
    movements: List[BridgeMovementOut] = []
    why: str


# The class BudgetSuggestionOut is a schema for one budget worth revisiting.
class BudgetSuggestionOut(Schema):
    # raise | lower | create | overlap
    kind: str
    budget_id: Optional[int] = None
    budget_name: str
    tag_names: List[str] = []
    budgeted_per_year: AmountDecimal
    measured_per_year: AmountDecimal
    suggested_per_year: AmountDecimal
    suggested_amount: AmountDecimal
    cadence: str
    per_paycheck_effect: AmountDecimal
    bucket_name: Optional[str] = None
    why: str


# The class LeverOut is a schema for what could close an unfixable gap.
class LeverOut(Schema):
    kind: str
    what: str
    amount_per_paycheck: AmountDecimal
    detail: str


# The class SavingsPlanOut is a schema representing a whole savings plan.
class SavingsPlanOut(Schema):
    generated_for: date
    horizon_months: int
    buffer: AmountDecimal
    paychecks_in_horizon: int

    # Three figures answering three questions: what the plan allocates to, what
    # needs no bridging at all, and what the year affords.
    capacity_per_paycheck: AmountDecimal
    path_capacity_per_paycheck: AmountDecimal
    horizon_capacity_per_paycheck: AmountDecimal

    minimums_total: AmountDecimal
    targets_total: AmountDecimal
    planned_total: AmountDecimal
    current_total: AmountDecimal
    unallocated: AmountDecimal
    # What the plan frees against what is contributed today, and what is being
    # put away that no stated minimum or target asked for.
    freed_per_paycheck: AmountDecimal
    optional_per_paycheck: AmountDecimal

    feasible: bool
    verified: bool
    timing_shortfall: Optional[DipOut] = None

    lines: List[PlanLineOut] = []
    breaches: List[DipOut] = []
    bridges: List[BridgeOut] = []
    budget_suggestions: List[BudgetSuggestionOut] = []
    levers: List[LeverOut] = []
    notes: List[str] = []

    model_config = ConfigDict(from_attributes=True)
