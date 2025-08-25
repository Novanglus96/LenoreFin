from ninja import Schema
from typing import Optional
from pydantic import ConfigDict


# The class ContribRuleIn is a schema for validating Contribution Rules.
class ContribRuleIn(Schema):
    rule: str
    cap: Optional[str] = None
    order: Optional[int] = 0


# The class ContribRuleOut is a schema representing Contribution Rules.
class ContribRuleOut(Schema):
    id: int
    rule: str
    cap: Optional[str] = None
    order: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)
