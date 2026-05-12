from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from reminders.dto import DomainRepeat
from typing import List, Optional
from transactions.dto import DomainTransaction
from accounts.dto import DomainGraphData


@dataclass
class DomainBudget:
    id: int
    tag_ids: str
    name: str
    amount: Decimal
    roll_over: bool
    repeat: DomainRepeat
    start_day: date
    roll_over_amt: Decimal
    active: bool
    widget: bool
    next_start: date


@dataclass
class DomainCalculationRule:
    id: int
    tag_ids: str
    name: str
    source_account_id: int
    destination_account_id: int


@dataclass
class DomainCalculator:
    rule: DomainCalculationRule
    transfers: List[DomainTransaction]
    transactions: List[DomainTransaction]


@dataclass
class DomainContribRule:
    id: int
    rule: str
    cap: Optional[str] = None
    order: Optional[int] = 0


@dataclass
class DomainContribution:
    id: int
    contribution: str
    per_paycheck: Decimal
    emergency_diff: Decimal
    emergency_amt: Decimal
    cap: Decimal
    active: bool


@dataclass
class DomainContributionWithTotals:
    contributions: List[DomainContribution]
    per_paycheck_total: Decimal
    emergency_paycheck_total: Decimal
    total_emergency: Decimal


@dataclass
class DomainNote:
    id: int
    note_text: str
    note_date: date


@dataclass
class DomainPlanningGraph:
    data: DomainGraphData
    year1: int
    year2: int
    year1_avg: Decimal
    year2_avg: Decimal
    pretty_name: str
    key_name: str


@dataclass
class DomainPlanningGraphList:
    title: str
    data: List[DomainPlanningGraph]


@dataclass
class DomainTargetObject:
    value: int


@dataclass
class DomainFillObject:
    target: DomainTargetObject
    above: str
    below: str


@dataclass
class DomainDataSetObject:
    borderColor: Optional[str] = None
    backgroundColor: Optional[str] = None
    tension: Optional[Decimal] = None
    data: Optional[List[Decimal]] = None
    pointStyle: Optional[str] = None
    radius: Optional[int] = None
    hitRadius: Optional[int] = None
    hoverRadius: Optional[int] = None
    label: Optional[str] = None
    hoverBackgroundColor: Optional[str] = "rgba(75,192,192,0.6)"
    hoverBorderColor: Optional[str] = "rgba(75,192,192,1)"
    fill: Optional[bool] = None


@dataclass
class DomainGraphData:
    labels: List[str]
    datasets: List[DomainDataSetObject]


@dataclass
class DomainForecast:
    labels: List[str]
    datasets: List[DomainDataSetObject]
