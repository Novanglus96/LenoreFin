from ninja import Schema
from typing import Optional
from administration.api.schemas.error_level import ErrorLevelOut
from administration.api.schemas.graph_type import GraphTypeOut
from pydantic import ConfigDict, condecimal

BalanceDecimal = condecimal(max_digits=12, decimal_places=2)


# The class OptionIn is a schema for validating Options.
class OptionIn(Schema):
    log_level_id: Optional[int] = None
    alert_balance: Optional[BalanceDecimal] = None
    alert_period: Optional[int] = None
    widget1_graph_name: Optional[str] = None
    widget1_tag_id: Optional[int] = None
    widget1_type_id: Optional[int] = None
    widget1_month: Optional[int] = 0
    widget1_exclude: Optional[str] = None
    widget2_graph_name: Optional[str]
    widget2_tag_id: Optional[int] = None
    widget2_type_id: Optional[int] = None
    widget2_month: Optional[int] = 0
    widget2_exclude: Optional[str] = None
    widget3_graph_name: Optional[str]
    widget3_tag_id: Optional[int] = None
    widget3_type_id: Optional[int] = None
    widget3_month: Optional[int] = 0
    widget3_exclude: Optional[str] = None
    auto_archive: Optional[bool] = True
    archive_length: Optional[str] = 2
    enable_cc_bill_calculation: Optional[bool] = True
    report_main: Optional[str] = None
    report_individual: Optional[str] = None
    retirement_accounts: Optional[str] = None


# The class OptionOut is a schema for representing Options.
class OptionOut(Schema):
    id: int
    log_level: ErrorLevelOut
    alert_balance: BalanceDecimal = None
    alert_period: int
    widget1_graph_name: str
    widget1_tag_id: Optional[int] = None
    widget1_type: Optional[GraphTypeOut] = None
    widget1_month: int = 0
    widget1_exclude: Optional[str] = None
    widget2_graph_name: str
    widget2_tag_id: Optional[int] = None
    widget2_type: Optional[GraphTypeOut] = None
    widget2_month: int = 0
    widget2_exclude: Optional[str] = None
    widget3_graph_name: str
    widget3_tag_id: Optional[int] = None
    widget3_type: Optional[GraphTypeOut] = None
    widget3_month: int = 0
    widget3_exclude: Optional[str] = None
    auto_archive: Optional[bool] = True
    archive_length: Optional[int] = 2
    enable_cc_bill_calculation: Optional[bool] = True
    report_main: Optional[str] = None
    report_individual: Optional[str] = None
    retirement_accounts: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
