from ninja import Schema
from typing import List, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field


# The class GraphDataset is a schema for representing graph datasets.
class GraphDataset(Schema):
    label: str
    data: List[Decimal] = Field(whole_digits=10, decimal_places=2)
    backgroundColor: List[str]
    hoverOffset: int = 4


# The class GraphOut is a schema for representing Graphs.
class GraphOut(Schema):
    labels: List[str]
    datasets: List[GraphDataset]
