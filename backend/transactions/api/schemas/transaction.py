from ninja import Schema
from pydantic import ConfigDict, condecimal
from datetime import date
from typing import List, Optional
from tags.api.schemas.tag import TagDetailIn
from transactions.api.schemas.paycheck import PaycheckIn, PaycheckOut
from transactions.api.schemas.transaction_status import TransactionStatusOut
from transactions.api.schemas.transaction_type import TransactionTypeOut
from tags.api.schemas.tag import TagOut
from decimal import Decimal
from pydantic import field_serializer
from moneyed import Money


class MoneyOut(Schema):
    amount: Decimal
    currency: str


AmountDecimal = condecimal(max_digits=12, decimal_places=2)


# The class TransactionIn is a schema for validating Transaction information.
class TransactionIn(Schema):
    transaction_date: date
    total_amount: AmountDecimal
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
class TransactionList(Schema):
    transactions: List[int]


# The class MultiTransactionDate is a schema for editing dates of transactions.
class MultiTranscationDate(Schema):
    transaction_ids: List[int]
    new_date: date
    edit_date: Optional[date] = None


# The class TransactionOut is a schema for representing Transactions.
class TransactionOut(Schema):
    id: int
    transaction_date: date
    total_amount: MoneyOut
    status: TransactionStatusOut
    memo: Optional[str] = None
    description: str
    edit_date: date
    add_date: date
    transaction_type: TransactionTypeOut
    paycheck: Optional[PaycheckOut] = None
    balance: Optional[AmountDecimal] = None
    pretty_account: Optional[str] = None
    tags: Optional[List[Optional[str]]] = []
    details: List["TransactionDetailOut"] = []
    pretty_total: Optional[AmountDecimal] = None
    source_account_id: Optional[int] = None
    destination_account_id: Optional[int] = None
    checkNumber: Optional[int] = None
    reminder_id: Optional[int] = None
    tag_total: Optional[AmountDecimal] = None
    simulated: Optional[bool] = False

    @field_serializer("total_amount")
    def serialize_money(self, money: Money, _info):
        return {
            "amount": money.amount,
            "currency": money.currency.code,
        }

    model_config = ConfigDict(from_attributes=True)


from transactions.api.schemas.transaction_detail import (  # noqa: E402
    TransactionDetailOut,  # noqa: E402
)  # noqa: E402

TransactionOut.update_forward_refs()


# The class TagTransactionOut is a schema for representing Transactions by Tag.
class TagTransactionOut(Schema):
    transaction: TransactionOut
    detail_amt: AmountDecimal
    pretty_account: str
    tag: TagOut


# The class PaginatedTransactions is a schema for validating paginated transactions.
class PaginatedTransactions(Schema):
    transactions: List[TransactionOut]
    current_page: int
    total_pages: int
    total_records: int

    model_config = ConfigDict(from_attributes=True)


class TransactionQuery(Schema):
    view_type: Optional[int] = 2
    account: Optional[int] = None
    maxdays: Optional[int] = 14
    forecast: Optional[bool] = False
    page: Optional[int] = 1
    page_size: Optional[int] = 60
    rule_id: Optional[int] = None
