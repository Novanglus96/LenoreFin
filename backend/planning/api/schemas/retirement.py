from ninja import Schema
from typing import List, Optional
from pydantic import condecimal
from datetime import date
from decimal import Decimal

TensionDecimal = condecimal(max_digits=2, decimal_places=1)
DataDecimal = condecimal(max_digits=12, decimal_places=2)


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
    borderColor: Optional[str] = None
    backgroundColor: Optional[str] = None
    tension: Optional[TensionDecimal] = None
    data: Optional[List[DataDecimal]] = None
    pointStyle: Optional[str] = None
    radius: Optional[int] = None
    hitRadius: Optional[int] = None
    hoverRadius: Optional[int] = None
    label: Optional[str] = None
    hoverBackgroundColor: Optional[str] = "rgba(75,192,192,0.6)"
    hoverBorderColor: Optional[str] = "rgba(75,192,192,1)"
    fill: Optional[bool] = None


# The class GraphData is a schema representing a graph data object.
class GraphData(Schema):
    labels: List[str]
    datasets: List[DatasetObject]


# The class ForecastOut is a schema for representing forecast graph data.
class ForecastOut(Schema):
    labels: List[str]
    datasets: List[DatasetObject]


class RetirementTransactionOut(Schema):
    transaction_date: date
    account_name: str
    description: str
    total_amount: Decimal
    balance: Optional[Decimal] = None
    status_name: str
    transaction_type_name: str

    model_config = {"from_attributes": True}
