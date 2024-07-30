from ninja import Schema
from datetime import date, timedelta, datetime
from typing import List, Optional, Dict, Any
from accounts.api.schemas.account import AccountOut
from reminders.api.schemas.reminder import ReminderOut
from transactions.api.schemas.transaction import TransactionOut
from administration.api.schemas.error_level import ErrorLevelOut


# The class LogEntryIn is a schema for validating Log Entries.
class LogEntryIn(Schema):
    log_date: Optional[datetime] = None
    log_entry: str
    account_id: Optional[int] = None
    reminder_id: Optional[int] = None
    transaction_id: Optional[int] = None
    error_num: Optional[int] = None
    error_level_id: Optional[int] = None


# The class LogEntryOut is a schema for representing Log Entries.
class LogEntryOut(Schema):
    log_date: datetime
    log_entry: str
    account: Optional[AccountOut] = None
    reminder: Optional[ReminderOut] = None
    transaction: Optional[TransactionOut] = None
    error_num: Optional[int] = None
    error_level: Optional[ErrorLevelOut] = None
