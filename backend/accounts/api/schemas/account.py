from ninja import Schema
from pydantic import Field
from typing import Optional
from decimal import Decimal
from datetime import date
from accounts.api.schemas.account_type import AccountTypeOut
from accounts.api.schemas.bank import BankOut


# The class AccountIn is a schema for validating accounts.
class AccountIn(Schema):
    account_name: str
    account_type_id: int
    opening_balance: Optional[Decimal] = Field(
        whole_digits=10, decimal_places=2
    )
    apy: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)
    due_date: Optional[date]
    active: bool
    open_date: Optional[date]
    next_cycle_date: Optional[date]
    statement_cycle_length: Optional[int]
    statement_cycle_period: Optional[str]
    credit_limit: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)
    bank_id: int
    last_statement_amount: Optional[Decimal] = Field(
        whole_digits=2, decimal_places=2
    )


# The class AccountUpdate is a schema for updating account information.
class AccountUpdate(Schema):
    account_name: Optional[str]
    account_type_id: Optional[int]
    opening_balance: Optional[Decimal] = Field(
        whole_digits=10, decimal_places=2
    )
    apy: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)
    due_date: Optional[date]
    active: Optional[bool]
    open_date: Optional[date]
    next_cycle_date: Optional[date]
    statement_cycle_length: Optional[int]
    statement_cycle_period: Optional[str]
    credit_limit: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)
    bank_id: Optional[int]
    last_statement_amount: Optional[Decimal] = Field(
        whole_digits=2, decimal_places=2
    )
    rewards_amount: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)


# The class AccountOut is a schema for representing accounts.
class AccountOut(Schema):
    id: int
    account_name: str
    account_type: AccountTypeOut
    opening_balance: Decimal = Field(whole_digits=10, decimal_places=2)
    apy: Decimal = Field(whole_digits=2, decimal_places=2)
    due_date: Optional[date]
    active: bool
    open_date: date
    next_cycle_date: Optional[date]
    statement_cycle_length: Optional[int]
    statement_cycle_period: Optional[str]
    rewards_amount: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)
    credit_limit: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)
    available_credit: Optional[Decimal] = Field(
        whole_digits=2, decimal_places=2
    )
    balance: Optional[Decimal] = Field(whole_digits=10, decimal_places=2)
    bank: BankOut
    last_statement_amount: Optional[Decimal] = Field(
        whole_digits=2, decimal_places=2
    )
