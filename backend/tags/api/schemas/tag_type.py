from ninja import Schema


# The class TagTypeIn is a schema for validating tag types.
class TagTypeIn(Schema):
    tag_type: str


# The class TagTypeOut is a schema for representing tag types.
class TagTypeOut(Schema):
    id: int
    tag_type: str
