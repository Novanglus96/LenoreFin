from dataclasses import dataclass
from typing import Optional
from tags.dto import DomainTag
from accounts.dto import DomainAccount
from transactions.dto import DomainTransactionType
from decimal import Decimal
from datetime import date


@dataclass
class DomainRepeat:
    id: int
    repeat_name: str
    days: Optional[int] = 0
    weeks: Optional[int] = 0
    months: Optional[int] = 0
    years: Optional[int] = 0


@dataclass
class DomainReminder:
    id: int
    tag: DomainTag
    amount: Decimal
    reminder_source_account: DomainAccount
    reminder_destination_account: Optional[DomainAccount] = None
    description: str
    transaction_type: DomainTransactionType
    start_date: date
    next_date: Optional[date] = None
    end_date: Optional[date] = None
    repeat: DomainRepeat
    auto_add: bool
    memo: Optional[str] = None
