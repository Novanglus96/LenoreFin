from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, List
from accounts.dto import DomainGraphData

if TYPE_CHECKING:
    from transactions.dto import DomainTransaction


@dataclass
class DomainTagType:
    id: int
    tag_type: str


@dataclass
class DomainMainTag:
    id: int
    tag_name: str
    tag_type: DomainTagType


@dataclass
class DomainSubTag:
    id: int
    tag_name: str
    tag_type: DomainTagType


@dataclass
class DomainTag:
    id: int
    tag_name: str
    parent: DomainMainTag
    child: DomainSubTag | None = None
    tag_type: DomainTagType | None = None


@dataclass
class DomainGraphDataset:
    label: str
    data: List[Decimal]
    backgroundColor: List[str]
    hoverOffset: int = 4


@dataclass
class DomainGraph:
    labels: List[str]
    datasets: List[DomainGraphDataset]


@dataclass
class DomainPieGraphItem:
    key: int
    title: str
    value: Decimal
    color: str
    total: Decimal = 0


@dataclass
class DomainTagGraph:
    data: DomainGraphData
    year1: int
    year2: int
    year1_avg: Decimal
    year2_avg: Decimal
    transactions: List[DomainTransaction]
