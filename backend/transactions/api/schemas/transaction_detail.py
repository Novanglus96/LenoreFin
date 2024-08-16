from typing import TYPE_CHECKING
from ninja import Schema
from decimal import Decimal
from pydantic import BaseModel, Field
from tags.api.schemas.tag import TagOut


# The class TransactionDetailOut is a schema for representing Transaction Details.
class TransactionDetailOut(Schema):
    id: int
    transaction: "TransactionOut"
    detail_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    tag: TagOut
    full_toggle: bool


from transactions.api.schemas.transaction import TransactionOut

TransactionDetailOut.update_forward_refs()


# The class TransactionDetailIn is a schema for validating Transaction Details.
class TransactionDetailIn(Schema):
    transaction_id: int
    account_id: int
    detail_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    tag_id: int
    full_toggle: bool
