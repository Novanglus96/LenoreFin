from ninja import Schema
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import date, timedelta, datetime
from typing import List, Optional, Dict, Any


# The class TypeMappingSchema is a schema for representing import type mappings.
class TypeMappingSchema(Schema):
    file_type: str
    type_id: int


# The class StatusMappingSchema is a schema for representing import status mappings.
class StatusMappingSchema(Schema):
    file_status: str
    status_id: int


# The class AccountMappingSchema is a schema for representing import account mappings.
class AccountMappingSchema(Schema):
    file_account: str
    account_id: int


# The class TagMapping is a schema for representing import tag mappings.
class TagMappingSchema(Schema):
    file_tag: str
    tag_id: int


# The class TransactionImportTagSchema is a schema for representing import transaction tags.
class TransactionImportTagSchema(Schema):
    tag_id: int
    tag_name: str
    tag_amount: Decimal = Field(whole_digits=10, decimal_places=2)


# The class TransactionImportErrorSchema is a schema for representing import transaction errors.
class TransactionImportErrorSchema(Schema):
    text: str
    status: int


# The class TransactionImportSchema is a schema for representing import transactions.
class TransactionImportSchema(Schema):
    line_id: int
    transactionDate: date
    transactionTypeID: int
    transactionStatusID: int
    amount: Decimal = Field(whole_digits=10, decimal_places=2)
    description: str
    sourceAccountID: int
    destinationAccountID: Optional[int] = None
    tags: List[TransactionImportTagSchema]
    memo: str
    errors: List[TransactionImportErrorSchema]


# The class MappingDefinition is a schema for representing import mappings.
class MappingDefinition(Schema):
    transaction_types: List[TypeMappingSchema]
    transaction_statuses: List[StatusMappingSchema]
    accounts: List[AccountMappingSchema]
    tags: List[TagMappingSchema]
    transactions: List[TransactionImportSchema]
