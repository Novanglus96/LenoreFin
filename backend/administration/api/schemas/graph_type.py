from ninja import Schema
from pydantic import ConfigDict


# The class GraphTypeOut is a schema for validating Graph Types.
class GraphTypeOut(Schema):
    id: int
    graph_type: str
    slug: str
    is_system: bool

    model_config = ConfigDict(from_attributes=True)
