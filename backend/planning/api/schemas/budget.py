from ninja import Schema
from typing import List, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field
from reminders.api.schemas.repeat import RepeatOut
from datetime import date, timedelta, datetime
from transactions.api.schemas.transaction import TransactionOut


# The class BudgetIn is a schema for validating Budgets.
class BudgetIn(Schema):
    tag_ids: str
    name: str
    amount: Decimal = Field(whole_digits=10, decimal_places=2)
    roll_over: bool
    repeat_id: int
    start_day: date
    roll_over_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    active: bool
    widget: bool
    next_start: date


# The class BudgetOut is a schema for representing Budgets.
class BudgetOut(Schema):
    id: int
    tag_ids: str
    name: str
    amount: Decimal = Field(whole_digits=10, decimal_places=2)
    roll_over: bool
    repeat: RepeatOut
    start_day: date
    roll_over_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    active: bool
    widget: bool
    next_start: date


# The class BudgetTotals is a schema for representing Budgets with totals.
class BudgetWithTotal(Schema):
    budget: BudgetOut
    transactions: List[TransactionOut]
    used_total: Decimal = Field(whole_digits=10, decimal_places=2)
    used_percentage: int
