from ninja import Schema
from pydantic import ConfigDict, condecimal
from transactions.api.schemas.transaction import TagTransactionOut
from accounts.api.schemas.forecast import GraphData
from typing import List

AverageDecimal = condecimal(max_digits=12, decimal_places=2)


# The class TagGraphOut is a schema for representing a tag bar graph data.
class TagGraphOut(Schema):
    data: GraphData
    year1: int
    year2: int
    year1_avg: AverageDecimal
    year2_avg: AverageDecimal
    transactions: List[TagTransactionOut]

    model_config = ConfigDict(from_attributes=True)
