from ninja import Schema
from typing import Optional
from tags.api.schemas.tag import TagOut
from pydantic import ConfigDict


# The class DescriptionHistoryOut is a schema for representing description history.
class DescriptionHistoryOut(Schema):
    id: int
    description_pretty: str
    tag: Optional[TagOut] = None

    model_config = ConfigDict(from_attributes=True)
