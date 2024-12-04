from ninja import Schema
from typing import List, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field


# The class TargetObject is a schema representing a FillObject Target.
class TargetObject(Schema):
    value: int


# The class FillObject is a schema representing a Dataset FillObject.
class FillObject(Schema):
    target: TargetObject
    above: str
    below: str


# The class DatasetObject is a schema representing a Graph Forecast Dataset.
class DatasetObject(Schema):
    borderColor: Optional[str]
    backgroundColor: Optional[str]
    tension: Optional[Decimal] = Field(whole_digits=1, decimal_places=1)
    data: Optional[List[Decimal]] = Field(whole_digits=10, decimal_places=2)
    pointStyle: Optional[str]
    radius: Optional[int]
    hitRadius: Optional[int]
    hoverRadius: Optional[int]
    label: Optional[str]
    hoverBackgroundColor: Optional[str] = "rgba(75,192,192,0.6)"
    hoverBorderColor: Optional[str] = "rgba(75,192,192,1)"


# The class GraphData is a schema representing a graph data object.
class GraphData(Schema):
    labels: List[str]
    datasets: List[DatasetObject]


# The class ForecastOut is a schema for representing forecast graph data.
class ForecastOut(Schema):
    labels: List[str]
    datasets: List[DatasetObject]
