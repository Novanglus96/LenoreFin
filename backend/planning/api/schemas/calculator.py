from ninja import Schema
from datetime import date, timedelta, datetime


# The class CalculationRuleIn is a schema for validating a calcuation
# rule.
class CalculationRuleIn(Schema):
    tag_ids: str
    name: str
    source_account_id: int
    destination_account_id: int


# The class CalculationRuleOut is a schema for representing a calculation
# rule.
class CalculationRuleOut(Schema):
    id: int
    tag_ids: str
    name: str
    source_account_id: int
    destination_account_id: int
