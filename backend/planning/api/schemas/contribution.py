from ninja import Schema
from typing import List, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field


# The class ContributionIn is a schema for validating Contributions.
class ContributionIn(Schema):
    contribution: str
    per_paycheck: Decimal = Field(whole_digits=10, decimal_places=2)
    emergency_diff: Decimal = Field(whole_digits=10, decimal_places=2)
    emergency_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    cap: Decimal = Field(whole_digits=10, decimal_places=2)
    active: bool


# The class ContributionOut is a schema for representing Contributions.
class ContributionOut(Schema):
    id: int
    contribution: str
    per_paycheck: Decimal = Field(whole_digits=10, decimal_places=2)
    emergency_diff: Decimal = Field(whole_digits=10, decimal_places=2)
    emergency_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    cap: Decimal = Field(whole_digits=10, decimal_places=2)
    active: bool


# The class ContributionsWithTotals is a schema for representing Contributions
# with totals
class ContributionWithTotals(Schema):
    contributions: List[ContributionOut]
    per_paycheck_total: Decimal = Field(whole_digits=10, decimal_places=2)
    emergency_paycheck_total: Decimal = Field(whole_digits=10, decimal_places=2)
    total_emergency: Decimal = Field(whole_digits=10, decimal_places=2)
