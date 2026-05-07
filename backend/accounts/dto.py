from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date
from typing import List, Optional


@dataclass
class DomainAccountType:
    id: int
    account_type: str
    color: str
    icon: str


@dataclass
class DomainBank:
    id: int
    bank_name: str


@dataclass
class DomainAccount:
    id: int
    account_name: str
    account_type: DomainAccountType
    opening_balance: Decimal
    annual_rate: Decimal
    active: bool
    open_date: date
    bank: DomainBank
    current_yr_rewards: List[Decimal] = field(default_factory=list)
    last_yr_rewards: List[Decimal] = field(default_factory=list)
    due_date: Optional[date] = None
    statement_date: Optional[date] = None
    statement_cycle_length: Optional[int] = None
    statement_cycle_period: Optional[int] = None
    credit_limit: Optional[Decimal] = None
    rewards_amount: Optional[Decimal] = None
    available_credit: Optional[Decimal] = None
    balance: Optional[Decimal] = None
    last_statement_amount: Optional[Decimal] = None
    funding_account: Optional[DomainAccount] = None
    calculate_payments: Optional[bool] = False
    calculate_interest: Optional[bool] = False
    payment_strategy: Optional[str] = None
    payment_amount: Optional[Decimal] = None
    minimum_payment_amount: Optional[Decimal] = None
    statement_day: Optional[int] = 15
    due_day: Optional[int] = 15
    pay_day: Optional[int] = 15


@dataclass
class DomainTargetObject:
    value: int


@dataclass
class DomainFillObject:
    target: DomainTargetObject
    above: str
    below: str


@dataclass
class DomainDatasetObject:
    borderColor: Optional[str] = None
    backgroundColor: Optional[str] = None
    tension: Optional[Decimal] = None
    data: Optional[List[Decimal]] = None
    fill: Optional[DomainFillObject] = None
    pointStyle: Optional[str] = None
    radius: Optional[int] = None
    hitRadius: Optional[int] = None
    hoverRadius: Optional[int] = None
    label: Optional[str] = None
    hoverBackgroundColor: Optional[str] = "rgba(75,192,192,0.6)"
    hoverBorderColor: Optional[str] = "rgba(75,192,192,1)"


@dataclass
class DomainGraphData:
    labels: List[str]
    datasets: List[DomainDatasetObject]


@dataclass
class DomainForecast:
    labels: List[str]
    datasets: List[DomainDatasetObject]
