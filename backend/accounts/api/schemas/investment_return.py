from ninja import Schema
from typing import Optional


class InvestmentReturnOut(Schema):
    rate: Optional[float] = None
    period_months: int
    data_points: int
    sufficient_data: bool
