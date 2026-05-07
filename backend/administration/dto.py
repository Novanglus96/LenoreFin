from dataclasses import dataclass
from tags.dto import DomainTag
from typing import Optional, List
from datetime import date
from decimal import Decimal


@dataclass
class DomainPayee:
    id: int
    payee_name: str


@dataclass
class DomainDescriptionHistory:
    id: int
    description_pretty: str
    tag: Optional[DomainTag] = None


@dataclass
class DomainGraphType:
    id: int
    graph_type: str


@dataclass
class DomainMessage:
    id: int
    message_date: date
    message: str
    unread: bool


@dataclass
class DomainMessageList:
    unread_count: int
    total_count: int
    messages: List[DomainMessage]


@dataclass
class DomainOption:
    id: int
    alert_period: int
    widget1_graph_name: str
    widget2_graph_name: str
    widget3_graph_name: str
    alert_balance: Optional[Decimal] = None
    widget1_month: int = 0
    widget2_month: int = 0
    widget3_month: int = 0
    widget1_tag_id: Optional[int] = None
    widget1_type: Optional[DomainGraphType] = None
    widget1_exclude: Optional[str] = None
    widget2_tag_id: Optional[int] = None
    widget2_type: Optional[DomainGraphType] = None
    widget2_exclude: Optional[str] = None
    widget3_tag_id: Optional[int] = None
    widget3_type: Optional[DomainGraphType] = None
    widget3_exclude: Optional[str] = None
    auto_archive: Optional[bool] = True
    archive_length: Optional[int] = 2
    enable_cc_bill_calculation: Optional[bool] = True
    report_main: Optional[str] = None
    report_individual: Optional[str] = None
    retirement_accounts: Optional[str] = None


@dataclass
class DomainVersion:
    id: int
    version_number: str
