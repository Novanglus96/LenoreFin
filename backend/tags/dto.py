from __future__ import annotations
from dataclasses import dataclass


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
