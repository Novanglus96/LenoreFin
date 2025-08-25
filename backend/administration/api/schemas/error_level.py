from ninja import Schema
from pydantic import ConfigDict


# The class ErrorLevelIn is a schema for validating Error Levels.
class ErrorLevelIn(Schema):
    error_level: str


# The class ErrorLevelOut is a schema for representing Error Levels.
class ErrorLevelOut(Schema):
    id: int
    error_level: str

    model_config = ConfigDict(from_attributes=True)
