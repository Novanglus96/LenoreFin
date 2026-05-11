from ninja import Schema
from tags.api.schemas.tag_type import TagTypeOut
from pydantic import ConfigDict
from typing import Optional


# The class SubTagIn is a schema for validating sub tags.
class SubTagIn(Schema):
    tag_name: str
    tag_type_id: int


# the class SubTagOut is a schema for representing sub tags.
class SubTagOut(Schema):
    id: int
    tag_name: str
    tag_type: TagTypeOut
    slug: str
    is_system: bool

    model_config = ConfigDict(from_attributes=True)


class SubTagQuery(Schema):
    tag_type: Optional[int] = None
    parent: Optional[int] = None
