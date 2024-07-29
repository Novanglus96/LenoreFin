from ninja import Schema
from decimal import Decimal
from typing import List, Optional, Dict, Any
from administration.api.schemas.error_level import ErrorLevelOut
from pydantic import BaseModel, Field


# The class OptionIn is a schema for validating Options.
class OptionIn(Schema):
    log_level_id: Optional[int]
    alert_balance: Optional[Decimal] = Field(whole_digits=10, decimal_places=2)
    alert_period: Optional[int]
    widget1_graph_name: Optional[str]
    widget1_tag_id: Optional[int] = None
    widget1_expense: Optional[bool] = True
    widget1_month: Optional[int] = 0
    widget1_exclude: Optional[str] = "[0]"
    widget2_graph_name: Optional[str]
    widget2_tag_id: Optional[int] = None
    widget2_expense: Optional[bool] = True
    widget2_month: Optional[int] = 0
    widget2_exclude: Optional[str] = "[0]"
    widget3_graph_name: Optional[str]
    widget3_tag_id: Optional[int] = None
    widget3_expense: Optional[bool] = True
    widget3_month: Optional[int] = 0
    widget3_exclude: Optional[str] = "[0]"


# The class OptionOut is a schema for representing Options.
class OptionOut(Schema):
    id: int
    log_level: ErrorLevelOut
    alert_balance: Decimal = Field(whole_digits=10, decimal_places=2)
    alert_period: int
    widget1_graph_name: str
    widget1_tag_id: Optional[int] = None
    widget1_expense: bool = True
    widget1_month: int = 0
    widget1_exclude: Optional[str] = "[0]"
    widget2_graph_name: str
    widget2_tag_id: Optional[int] = None
    widget2_expense: bool = True
    widget2_month: int = 0
    widget2_exclude: Optional[str] = "[0]"
    widget3_graph_name: str
    widget3_tag_id: Optional[int] = None
    widget3_expense: bool = True
    widget3_month: int = 0
    widget3_exclude: Optional[str] = "[0]"
