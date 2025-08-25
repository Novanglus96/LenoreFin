from ninja import Schema
from typing import List
from pydantic import ConfigDict, condecimal

DataDecimal = condecimal(max_digits=12, decimal_places=2)


# The class GraphDataset is a schema for representing graph datasets.
class GraphDataset(Schema):
    label: str
    data: List[DataDecimal]
    backgroundColor: List[str]
    hoverOffset: int = 4


# The class GraphOut is a schema for representing Graphs.
class GraphOut(Schema):
    labels: List[str]
    datasets: List[GraphDataset]

    model_config = ConfigDict(from_attributes=True)
