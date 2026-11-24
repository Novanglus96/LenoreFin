from datetime import date
from typing import Optional

from ninja import Schema
from pydantic import ConfigDict, condecimal

AmountDecimal = condecimal(max_digits=12, decimal_places=2)


class BucketIn(Schema):
    name: str
    contribution_per_paycheck: AmountDecimal = 0
    goal_amount: Optional[AmountDecimal] = None
    goal_date: Optional[date] = None
    active: bool = True
    account_id: Optional[int] = None
    reminder_id: Optional[int] = None


class BucketOut(Schema):
    id: int
    name: str
    contribution_per_paycheck: AmountDecimal
    goal_amount: Optional[AmountDecimal] = None
    goal_date: Optional[date] = None
    active: bool
    account_id: Optional[int] = None
    account_name: Optional[str] = None
    reminder_id: Optional[int] = None
    reminder_description: Optional[str] = None
    reminder_amount: Optional[AmountDecimal] = None

    model_config = ConfigDict(from_attributes=True)
