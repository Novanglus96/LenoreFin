from ninja import Schema
from typing import Optional
from pydantic import ConfigDict, condecimal
from datetime import date
from tags.api.schemas.tag import TagOut
from accounts.api.schemas.account import AccountOut
from transactions.api.schemas.transaction_type import TransactionTypeOut
from reminders.api.schemas.repeat import RepeatOut

AmountDecimal = condecimal(max_digits=12, decimal_places=2)


# The class ReminderIn is a schema for validating Reminders.
class ReminderIn(Schema):
    tag_id: int
    amount: AmountDecimal
    reminder_source_account_id: int
    reminder_destination_account_id: Optional[int] = None
    description: str
    transaction_type_id: int
    start_date: date
    next_date: Optional[date] = None
    end_date: Optional[date] = None
    repeat_id: int
    auto_add: bool
    memo: Optional[str] = None


# The class ReminderOut is a schema for representing Reminders.
class ReminderOut(Schema):
    id: int
    tag: TagOut
    amount: AmountDecimal
    reminder_source_account: AccountOut
    reminder_destination_account: Optional[AccountOut] = None
    description: str
    transaction_type: TransactionTypeOut
    start_date: date
    next_date: Optional[date] = None
    end_date: Optional[date] = None
    repeat: RepeatOut
    auto_add: bool
    memo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# The classs ReminderTransIn is a schema for adding reminder transactions.
class ReminderTransIn(Schema):
    transaction_date: date
