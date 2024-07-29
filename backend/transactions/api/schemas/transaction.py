from ninja import Schema
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import date, timedelta, datetime
from typing import List, Optional, Dict, Any
from tags.api.schemas.tag import TagDetailIn
from transactions.api.schemas.paycheck import PaycheckIn


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
