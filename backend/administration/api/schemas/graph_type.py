from ninja import Schema


# The class GraphTypeOut is a schema for validating Graph Types.
class GraphTypeOut(Schema):
    id: int
    graph_type: str
