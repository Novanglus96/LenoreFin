from ninja import Schema
from typing import List, Optional, Dict, Any


# The class RepeatIn is a schema for validating Repeat Intervals.
class RepeatIn(Schema):
    repeat_name: str
    days: Optional[int] = 0
    weeks: Optional[int] = 0
    months: Optional[int] = 0
    years: Optional[int] = 0


# The class RepeatOut is a schema for representing Repeat Intervals.
class RepeatOut(Schema):
    id: int
    repeat_name: str
    days: Optional[int] = 0
    weeks: Optional[int] = 0
    months: Optional[int] = 0
    years: Optional[int] = 0
