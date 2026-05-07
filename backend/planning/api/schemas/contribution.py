from ninja import Schema
from typing import List
from pydantic import ConfigDict, condecimal

AmountDecimal = condecimal(max_digits=12, decimal_places=2)


# The class ContributionIn is a schema for validating Contributions.
class ContributionIn(Schema):
    contribution: str
    per_paycheck: AmountDecimal
    emergency_diff: AmountDecimal
    emergency_amt: AmountDecimal
    cap: AmountDecimal
    active: bool


# The class ContributionOut is a schema for representing Contributions.
class ContributionOut(Schema):
    id: int
    contribution: str
    per_paycheck: AmountDecimal
    emergency_diff: AmountDecimal
    emergency_amt: AmountDecimal
    cap: AmountDecimal
    active: bool

    model_config = ConfigDict(from_attributes=True)


# The class ContributionsWithTotals is a schema for representing Contributions
# with totals
class ContributionWithTotals(Schema):
    contributions: List[ContributionOut]
    per_paycheck_total: AmountDecimal
    emergency_paycheck_total: AmountDecimal
    total_emergency: AmountDecimal

    model_config = ConfigDict(from_attributes=True)
