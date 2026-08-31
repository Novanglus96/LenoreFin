from ninja import Schema
from typing import List, Optional
from pydantic import ConfigDict, condecimal
from reminders.api.schemas.repeat import RepeatOut
from datetime import date
from transactions.api.schemas.transaction import TransactionOut

BalanceDecimal = condecimal(max_digits=12, decimal_places=2)


# The class BudgetIn is a schema for validating Budgets.
class BudgetIn(Schema):
    tag_ids: str
    name: str
    amount: BalanceDecimal
    roll_over: bool
    repeat_id: int
    start_day: date
    roll_over_amt: Optional[BalanceDecimal] = None
    active: bool
    widget: bool
    next_start: date
    # The budget this one is part of. Its amount is then a component of that
    # one's total rather than a figure of its own.
    parent_id: Optional[int] = None


# The class BudgetOut is a schema for representing Budgets.
class BudgetOut(Schema):
    id: int
    tag_ids: str
    name: str
    amount: BalanceDecimal
    roll_over: bool
    repeat: RepeatOut
    start_day: date
    roll_over_amt: BalanceDecimal
    active: bool
    widget: bool
    next_start: date
    parent_id: Optional[int] = None
    # What this budget actually plans to spend: the stored amount for a leaf,
    # the sum of the children for a parent.
    planned_amount: BalanceDecimal
    is_parent: bool

    model_config = ConfigDict(from_attributes=True)


# The class BudgetTotals is a schema for representing Budgets with totals.
class BudgetWithTotal(Schema):
    budget: BudgetOut
    transactions: List[TransactionOut]
    used_total: BalanceDecimal
    used_percentage: int
    remaining_percentage: int

    model_config = ConfigDict(from_attributes=True)


class BudgetQuery(Schema):
    widget: Optional[bool] = True
