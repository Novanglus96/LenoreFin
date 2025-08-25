from ninja import Schema
from tags.api.schemas.tag_type import TagTypeOut
from pydantic import ConfigDict


# The class MainTagIn is a schema for validating main tags.
class MainTagIn(Schema):
    tag_name: str
    tag_type_id: int


# The class MainTagOut is a schema for representing main tags.
class MainTagOut(Schema):
    id: int
    tag_name: str
    tag_type: TagTypeOut

    model_config = ConfigDict(from_attributes=True)
