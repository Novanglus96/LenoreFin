from ninja import Schema
from typing import Optional
from pydantic import ConfigDict


# The class WindfallRuleIn is a schema for validating Windfall Rules.
class WindfallRuleIn(Schema):
    rule: str
    cap: Optional[str] = None
    order: Optional[int] = 0


# The class WindfallRuleOut is a schema representing Windfall Rules.
class WindfallRuleOut(Schema):
    id: int
    rule: str
    cap: Optional[str] = None
    order: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)
