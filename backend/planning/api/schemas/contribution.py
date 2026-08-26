from ninja import Schema
from typing import List, Optional
from datetime import date
from decimal import Decimal
from pydantic import ConfigDict, condecimal

AmountDecimal = condecimal(max_digits=12, decimal_places=2)
RateDecimal = condecimal(max_digits=5, decimal_places=2)


# The class ContributionIn is a schema for validating Contributions.
class ContributionIn(Schema):
    contribution: str
    per_paycheck: AmountDecimal
    emergency_diff: AmountDecimal
    emergency_amt: AmountDecimal
    cap: AmountDecimal
    active: bool
    account_id: Optional[int] = None
    reminder_id: Optional[int] = None
    goal_type: str = "none"
    goal_amount: AmountDecimal = Decimal("0")
    goal_date: Optional[date] = None
    goal_rate: RateDecimal = Decimal("0")


# The class ContributionOut is a schema for representing Contributions.
class ContributionOut(Schema):
    id: int
    contribution: str
    per_paycheck: AmountDecimal
    emergency_diff: AmountDecimal
    emergency_amt: AmountDecimal
    cap: AmountDecimal
    active: bool
    account_id: Optional[int] = None
    reminder_id: Optional[int] = None
    goal_type: str
    goal_amount: AmountDecimal
    goal_date: Optional[date] = None
    goal_rate: RateDecimal
    # Convenience for the table, so it need not join accounts client-side.
    account_name: Optional[str] = None
    # What the linked reminder actually moves, against which per_paycheck is
    # compared to detect drift. None when no reminder is linked.
    reminder_amount: Optional[AmountDecimal] = None

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def resolve_account_name(obj):
        return obj.account.account_name if obj.account_id else None

    @staticmethod
    def resolve_reminder_amount(obj):
        return obj.reminder.amount if obj.reminder_id else None


# The class ContributionsWithTotals is a schema for representing Contributions
# with totals
class ContributionWithTotals(Schema):
    contributions: List[ContributionOut]
    per_paycheck_total: AmountDecimal
    emergency_paycheck_total: AmountDecimal
    total_emergency: AmountDecimal

    model_config = ConfigDict(from_attributes=True)
