from ninja import Schema
from pydantic import ConfigDict
from transactions.api.schemas.transaction import TransactionOut
from accounts.api.schemas.forecast import GraphData
from typing import List


# The class TagGraphOut is a schema for representing a tag bar graph data.
class TagGraphOut(Schema):
    data: GraphData
    year1: int
    year2: int
    year1_avg: float
    year2_avg: float
    transactions: List[TransactionOut]

    model_config = ConfigDict(from_attributes=True)
