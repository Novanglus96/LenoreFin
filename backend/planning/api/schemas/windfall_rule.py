from typing import Optional

from ninja import Schema
from pydantic import ConfigDict, condecimal

AmountDecimal = condecimal(max_digits=12, decimal_places=2)


class WindfallRuleIn(Schema):
    rule: str
    bucket_id: Optional[int] = None
    cap: Optional[str] = None
    cap_amount: Optional[AmountDecimal] = None
    order: int = 0


class WindfallRuleOut(Schema):
    id: int
    rule: str
    bucket_id: Optional[int] = None
    bucket_name: Optional[str] = None
    cap: Optional[str] = None
    cap_amount: Optional[AmountDecimal] = None
    order: int

    model_config = ConfigDict(from_attributes=True)
