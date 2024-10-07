from ninja import Schema
from decimal import Decimal
from pydantic import BaseModel, Field
from accounts.api.schemas.forecast import GraphData
from typing import List, Optional, Dict, Any


# The class PlanningGraphOut is a schema for representing a planning bar graph data.
class PlanningGraphOut(Schema):
    data: GraphData
    year1: int
    year2: int
    year1_avg: Decimal = Field(whole_digits=10, decimal_places=2)
    year2_avg: Decimal = Field(whole_digits=10, decimal_places=2)
    pretty_name: str
    key_name: str


# The class PlanningGraphOut is a schema for representing a planning bar graph data.
class PlanningGraphList(Schema):
    title: str
    data: List[PlanningGraphOut]
