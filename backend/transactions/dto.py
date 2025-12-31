from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List
from tags.dto import DomainTag
from administration.dto import DomainPayee


@dataclass
class DomainTransactionType:
    id: int
    transaction_type: str


@dataclass
class DomainTransactionStatus:
    id: int
    transaction_status: str


@dataclass
class DomainTransactionDetail:
    id: int
    transaction: DomainTransaction
    detail_amt: Decimal
    tag: DomainTag
    full_toggle: bool


@dataclass
class DomainPaycheck:
    id: int
    gross: Decimal
    net: Decimal
    taxes: Decimal
    health: Decimal
    pension: Decimal
    fsa: Decimal
    dca: Decimal
    union_dues: Decimal
    four_fifty_seven_b: Decimal
    payee: DomainPayee


@dataclass
class DomainTransaction:
    id: int
    transaction_date: date
    total_amount: Decimal
    status: DomainTransactionStatus
    memo: str | None = None
    description: str
    edit_date: date
    add_date: date
    transaction_type: DomainTransactionType
    paycheck: DomainPaycheck | None = None
    balance: Decimal | None = None
    pretty_account: str | None = None
    tags: List[str] | None = None
    details: List[DomainTransactionDetail] | None = None
    pretty_total: Decimal | None = None
    source_account_id: int
    destination_account_id: int | None = None
    checkNumber: int | None = None
    reminder_id: int | None = None
    tag_total: Decimal | None = None
    simulated: bool = False
