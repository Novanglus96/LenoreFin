from ninja import Schema
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal


class DetectedRecurringOut(Schema):
    id: int
    description: str
    estimated_amount: Decimal
    repeat_id: Optional[int] = None
    repeat_name: Optional[str] = None
    next_estimated_date: date
    transaction_ids: List[int]
    created_at: datetime
    suggested_tag_id: Optional[int] = None
    suggested_account_id: Optional[int] = None
