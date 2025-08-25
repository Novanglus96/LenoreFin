from ninja import Schema
from tags.api.schemas.main_tag import MainTagOut
from tags.api.schemas.tag_type import TagTypeOut
from tags.api.schemas.sub_tag import SubTagOut
from typing import Optional
from pydantic import ConfigDict, condecimal

AmountDecimal = condecimal(max_digits=12, decimal_places=2)


# The class TagIn is a schema for validating tags.
class TagIn(Schema):
    parent_id: Optional[int] = None
    parent_name: Optional[str] = None
    child_id: Optional[int] = None
    child_name: Optional[str] = None
    tag_type_id: int


# The class TagOut is a schema for representing tags.
class TagOut(Schema):
    id: int
    tag_name: str
    parent: MainTagOut
    child: Optional[SubTagOut] = None
    tag_type: Optional[TagTypeOut] = None

    model_config = ConfigDict(from_attributes=True)


# The class TagDetailIn is a schema for validating transaction tag details.
class TagDetailIn(Schema):
    tag_amt: AmountDecimal
    tag_pretty_name: str
    tag_id: int
    tag_full_toggle: bool
