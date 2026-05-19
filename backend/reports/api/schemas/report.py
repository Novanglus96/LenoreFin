from ninja import Schema
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal


class TagSelectionIn(Schema):
    tag_id: Optional[int] = None
    sub_tag_id: Optional[int] = None
    main_tag_id: Optional[int] = None


class TagSelectionOut(Schema):
    id: int
    tag_id: Optional[int] = None
    sub_tag_id: Optional[int] = None
    main_tag_id: Optional[int] = None


class ReportConfigIn(Schema):
    name: str
    description: str = ""
    report_type: str
    date_range_type: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    account_ids: List[int] = []
    group_by: str
    show_transactions: bool = False
    show_subtotal: bool = True
    include_pending: bool = False
    tag_selections: List[TagSelectionIn] = []


class ReportConfigOut(Schema):
    id: int
    name: str
    description: str
    report_type: str
    date_range_type: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    account_ids: List[int]
    group_by: str
    show_transactions: bool
    show_subtotal: bool
    include_pending: bool
    tag_selections: List[TagSelectionOut]
    created_at: datetime
    updated_at: datetime


class ReportRunIn(Schema):
    """Ad-hoc run payload — same fields as ReportConfigIn but no name required."""

    report_type: str
    date_range_type: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    account_ids: List[int] = []
    group_by: str
    show_transactions: bool = False
    show_subtotal: bool = True
    include_pending: bool = False
    tag_selections: List[TagSelectionIn] = []


class TransactionRowOut(Schema):
    id: int
    date: date
    description: str
    amount: Decimal
    account: str


class ReportRowOut(Schema):
    label: str
    total: Optional[Decimal] = None
    period1_total: Optional[Decimal] = None
    period2_total: Optional[Decimal] = None
    difference: Optional[Decimal] = None
    transactions: Optional[List[TransactionRowOut]] = None


class ReportResultOut(Schema):
    report_type: str
    group_by: str
    date_from: date
    date_to: date
    period2_from: Optional[date] = None
    period2_to: Optional[date] = None
    rows: List[ReportRowOut]
    subtotal: Optional[Decimal] = None
    subtotal2: Optional[Decimal] = None
