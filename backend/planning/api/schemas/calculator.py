from ninja import Schema
from transactions.api.schemas.transaction import TransactionOut
from typing import List
from pydantic import ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


# The class CalculatorOut is a schema for representing a calculator
class CalculatorOut(Schema):
    rule: CalculationRuleOut
    transfers: List[TransactionOut]
    transactions: List[TransactionOut]

    model_config = ConfigDict(from_attributes=True)
