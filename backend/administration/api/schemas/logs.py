from ninja import Schema
from typing import List


class LogEntryOut(Schema):
    timestamp: str
    level: str
    message: str


class LogPageOut(Schema):
    entries: List[LogEntryOut]
    total: int
    page: int
    pages: int
    log_type: str
