from ninja import Schema
from datetime import date, timedelta, datetime
from typing import List, Optional, Dict, Any


# The class MessageIn is a schema for validating Messages.
class MessageIn(Schema):
    message_date: datetime
    message: str
    unread: bool


# The class MessageOut is a schema for representing Messages.
class MessageOut(Schema):
    id: int
    message_date: datetime
    message: str
    unread: bool


# The class AllMessage is a schema for representing all messages.
class AllMessage(Schema):
    unread: bool


# The class MessageList is a schema for representing a list of Messages with unread and total count.
class MessageList(Schema):
    unread_count: int
    total_count: int
    messages: List[MessageOut]
