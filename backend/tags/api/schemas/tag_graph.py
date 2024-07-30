from ninja import Schema
from decimal import Decimal
from pydantic import BaseModel, Field
from transactions.api.schemas.transaction import TagTransactionOut
from accounts.api.schemas.forecast import GraphData
from typing import List, Optional, Dict, Any


# The class TagGraphOut is a schema for representing a tag bar graph data.
class TagGraphOut(Schema):
    data: GraphData
    year1: int
    year2: int
    year1_avg: Decimal = Field(whole_digits=10, decimal_places=2)
    year2_avg: Decimal = Field(whole_digits=10, decimal_places=2)
    transactions: List[TagTransactionOut]
