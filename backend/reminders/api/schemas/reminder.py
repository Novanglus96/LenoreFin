from ninja import Schema
from typing import List, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import date, timedelta, datetime
from tags.api.schemas.tag import TagOut
from accounts.api.schemas.account import AccountOut
from transactions.api.schemas.transaction_type import TransactionTypeOut
from reminders.api.schemas.repeat import RepeatOut


# The class ReminderIn is a schema for validating Reminders.
class ReminderIn(Schema):
    tag_id: int
    amount: Decimal = Field(whole_digits=10, decimal_places=2)
    reminder_source_account_id: int
    reminder_destination_account_id: Optional[int]
    description: str
    transaction_type_id: int
    start_date: date
    next_date: Optional[date]
    end_date: Optional[date]
    repeat_id: int
    auto_add: bool


# The class ReminderOut is a schema for representing Reminders.
class ReminderOut(Schema):
    id: int
    tag: TagOut
    amount: Decimal = Field(whole_digits=10, decimal_places=2)
    reminder_source_account: AccountOut
    reminder_destination_account: Optional[AccountOut]
    description: str
    transaction_type: TransactionTypeOut
    start_date: date
    next_date: Optional[date]
    end_date: Optional[date]
    repeat: RepeatOut
    auto_add: bool


# The classs ReminderTransIn is a schema for adding reminder transactions.
class ReminderTransIn(Schema):
    transaction_date: date
