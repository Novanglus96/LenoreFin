from ninja import Schema
from typing import List, Optional, Dict, Any


# The class ContribRuleIn is a schema for validating Contribution Rules.
class ContribRuleIn(Schema):
    rule: str
    cap: Optional[str] = None


# The class ContribRuleOut is a schema representing Contribution Rules.
class ContribRuleOut(Schema):
    id: int
    rule: str
    cap: Optional[str] = None
