from ninja import Schema
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import date, timedelta, datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from tags.api.schemas.tag import TagDetailIn
from transactions.api.schemas.paycheck import PaycheckIn, PaycheckOut
from administration.api.dependencies.get_todays_date_timezone_adjusted import (
    get_todays_date_timezone_adjusted,
)
from transactions.api.schemas.transaction_status import TransactionStatusOut
from transactions.api.schemas.transaction_type import TransactionTypeOut
from tags.api.schemas.tag import TagOut


# The class TransactionIn is a schema for validating Transaction information.
class TransactionIn(Schema):
    transaction_date: date
    total_amount: Decimal = Field(whole_digits=10, decimal_places=2)
    status_id: int
    memo: Optional[str] = None
    description: str
    edit_date: date
    add_date: date
    transaction_type_id: int
    paycheck_id: Optional[int] = None
    details: Optional[List[TagDetailIn]] = None
    source_account_id: Optional[int] = None
    destination_account_id: Optional[int] = None
    paycheck: Optional[PaycheckIn] = None
    checkNumber: Optional[int] = None


# The class TransactionClear is a schema for clearing Transactions.
class TransactionClear(Schema):
    id: int
    status_id: int
    edit_date: Optional[date] = None


# The class TransactionClearList is a schema for a list of clearing Transactions.
class TransactionClearList(Schema):
    transactions: List[int]


# The class TransactionOut is a schema for representing Transactions.
class TransactionOut(Schema):
    id: int
    transaction_date: date
    total_amount: Decimal = Field(whole_digits=10, decimal_places=2)
    status: TransactionStatusOut
    memo: Optional[str] = None
    description: str
    edit_date: date
    add_date: date
    transaction_type: TransactionTypeOut
    paycheck: Optional[PaycheckOut] = None
    balance: Optional[Decimal] = Field(
        default=None, whole_digits=10, decimal_places=2
    )
    pretty_account: Optional[str]
    tags: Optional[List[Optional[str]]] = []
    details: List["TransactionDetailOut"] = []
    pretty_total: Optional[Decimal] = Field(
        default=None, whole_digits=10, decimal_places=2
    )
    source_account_id: Optional[int] = None
    destination_account_id: Optional[int] = None
    checkNumber: Optional[int] = None
    reminder_id: Optional[int] = None


from transactions.api.schemas.transaction_detail import TransactionDetailOut

TransactionOut.update_forward_refs()


# The class TagTransactionOut is a schema for representing Transactions by Tag.
class TagTransactionOut(Schema):
    transaction: TransactionOut
    detail_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    pretty_account: str
    tag: TagOut


# The class PaginatedTransactions is a schema for validating paginated transactions.
class PaginatedTransactions(Schema):
    transactions: List[TransactionOut]
    current_page: int
    total_pages: int
    total_records: int
