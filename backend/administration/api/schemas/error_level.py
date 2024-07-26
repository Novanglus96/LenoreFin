from ninja import Schema


# The class ErrorLevelIn is a schema for validating Error Levels.
class ErrorLevelIn(Schema):
    error_level: str


# The class ErrorLevelOut is a schema for representing Error Levels.
class ErrorLevelOut(Schema):
    id: int
    error_level: str
