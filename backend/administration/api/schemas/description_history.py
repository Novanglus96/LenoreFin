from ninja import Schema
from typing import List, Optional, Dict, Any
from tags.api.schemas.tag import TagOut


# The class DescriptionHistoryOut is a schema for representing description history.
class DescriptionHistoryOut(Schema):
    id: int
    description_pretty: str
    tag: Optional[TagOut]
