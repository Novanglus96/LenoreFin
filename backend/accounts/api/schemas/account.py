from ninja import Schema
from typing import Optional
from datetime import date
from accounts.api.schemas.account_type import AccountTypeOut
from accounts.api.schemas.bank import BankOut
from pydantic import ConfigDict, condecimal

BalanceDecimal = condecimal(max_digits=12, decimal_places=2)
ApyDecimal = condecimal(max_digits=4, decimal_places=2)


# The class AccountIn is a schema for validating accounts.
class AccountIn(Schema):
    account_name: str
    account_type_id: int
    opening_balance: Optional[BalanceDecimal] = None
    apy: Optional[ApyDecimal] = None
    due_date: Optional[date] = None
    active: bool
    open_date: Optional[date] = None
    next_cycle_date: Optional[date]
    statement_cycle_length: Optional[int] = None
    statement_cycle_period: Optional[str] = None
    credit_limit: Optional[BalanceDecimal] = None
    bank_id: int
    last_statement_amount: Optional[BalanceDecimal] = None
    funding_account_id: Optional[int] = None
    calculate_payments: Optional[bool] = None
    calculate_interest: Optional[bool] = None
    payment_strategy: Optional[str] = None
    payment_amount: Optional[BalanceDecimal] = None
    minimum_payment_amount: Optional[BalanceDecimal] = None


# The class AccountOut is a schema for representing accounts.
class AccountOut(Schema):
    id: int
    account_name: str
    account_type: AccountTypeOut
    opening_balance: BalanceDecimal
    apy: ApyDecimal
    due_date: Optional[date] = None
    active: bool
    open_date: date
    next_cycle_date: Optional[date] = None
    statement_cycle_length: Optional[int] = None
    statement_cycle_period: Optional[str] = None
    rewards_amount: Optional[BalanceDecimal] = None
    available_credit: Optional[BalanceDecimal] = None
    balance: Optional[BalanceDecimal] = None
    bank: BankOut
    last_statement_amount: Optional[BalanceDecimal] = None
    funding_account: Optional["AccountOut"] = None
    calculate_payments: Optional[bool] = None
    calculate_interest: Optional[bool] = None
    payment_strategy: Optional[str] = None
    payment_amount: Optional[BalanceDecimal] = None
    minimum_payment_amount: Optional[BalanceDecimal] = None

    model_config = ConfigDict(from_attributes=True)


# The class AccountUpdate is a schema for updating account information.
class AccountUpdate(Schema):
    account_name: Optional[str] = None
    account_type_id: Optional[int] = None
    opening_balance: Optional[BalanceDecimal] = None
    apy: Optional[ApyDecimal] = None
    due_date: Optional[date] = None
    active: Optional[bool] = None
    open_date: Optional[date] = None
    next_cycle_date: Optional[date] = None
    statement_cycle_length: Optional[int] = None
    statement_cycle_period: Optional[str] = None
    credit_limit: Optional[BalanceDecimal] = None
    bank_id: Optional[int] = None
    last_statement_amount: Optional[BalanceDecimal] = None
    rewards_amount: Optional[BalanceDecimal] = None
    funding_account_id: Optional[int] = None
    calculate_payments: Optional[bool] = None
    calculate_interest: Optional[bool] = None
    payment_strategy: Optional[str] = None
    payment_amount: Optional[BalanceDecimal] = None
    minimum_payment_amount: Optional[BalanceDecimal] = None
