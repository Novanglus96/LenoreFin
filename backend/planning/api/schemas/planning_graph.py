from ninja import Schema
from pydantic import ConfigDict, condecimal
from accounts.api.schemas.forecast import GraphData
from typing import List

AverageDecimal = condecimal(max_digits=12, decimal_places=2)


# The class PlanningGraphOut is a schema for representing a planning bar graph data.
class PlanningGraphOut(Schema):
    data: GraphData
    year1: int
    year2: int
    year1_avg: AverageDecimal
    year2_avg: AverageDecimal
    pretty_name: str
    key_name: str

    model_config = ConfigDict(from_attributes=True)


# The class PlanningGraphOut is a schema for representing a planning bar graph data.
class PlanningGraphList(Schema):
    title: str
    data: List[PlanningGraphOut]
