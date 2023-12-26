from ninja import NinjaAPI, Schema
from api.models import Account, AccountType, CalendarDate, Tag, ChristmasGift, ContribRule, Contribution, ErrorLevel, TransactionType, Repeat, Reminder, Note, Option, TransactionStatus, Transaction, TransactionDetail, LogEntry
from typing import List, Optional
from django.shortcuts import get_object_or_404
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field

api = NinjaAPI()
api.title = "Money API"
api.version = "1.0.0"
api.description = "API documentation for Money"


class AccountTypeIn(Schema):
    account_type: str
    color: str
    icon: str


class AccountTypeOut(Schema):
    id: int
    account_type: str
    color: str
    icon: str


class AccountIn(Schema):
    account_name: str
    account_type: AccountTypeOut
    opening_balance: Decimal = Field(max_digits=10, decimal_places=2)
    apy: Decimal = Field(max_digits=2, decimal_places=2)
    due_date: Optional[date]
    active: bool
    open_date: date
    next_cycle_date: Optional[date]
    statement_cycle_length: Optional[int]
    rewards_amount: Optional[Decimal] = Field(max_digits=2, decimal_places=2)


class AccountOut(Schema):
    id: int
    account_name: str
    account_type: AccountTypeOut
    opening_balance: Decimal = Field(max_digits=10, decimal_places=2)
    apy: Decimal = Field(max_digits=2, decimal_places=2)
    due_date: Optional[date]
    active: bool
    open_date: date
    next_cycle_date: Optional[date]
    statement_cycle_length: Optional[int]
    rewards_amount: Optional[Decimal] = Field(max_digits=2, decimal_places=2)


class TagIn(Schema):
    tag_name: str
    parent_id: Optional[int] = None


class TagOut(Schema):
    id: int
    tag_name: str
    parent_id: Optional[int] = None


@api.post("/accounts/types")
def create_account_type(request, payload: AccountTypeIn):
    account_type = AccountType.objects.create(**payload.dict())
    return {"id": account_type.id}


@api.post("/accounts")
def create_account(request, payload: AccountIn):
    account = Account.objects.create(**payload.dict())
    return {"id": account.id}


@api.post("/tags")
def create_tag(request, payload: TagIn):
    tag = Tag.objects.create(**payload.dict())
    return {"id": tag.id}


@api.get("/accounts/types/{accounttype_id}", response=AccountTypeOut)
def get_account_type(request, accounttype_id: int):
    account_type = get_object_or_404(AccountType, id=accounttype_id)
    return account_type


@api.get("/accounts/{account_id}", response=AccountOut)
def get_account(request, account_id: int):
    account = get_object_or_404(Account, id=account_id)
    return account


@api.get("/tags/{tag_id}", response=TagOut)
def get_tag(request, tag_id: int):
    tag = get_object_or_404(Tag, id=tag_id)
    return tag


@api.get("/accounts/types", response=List[AccountTypeOut])
def list_account_types(request):
    qs = AccountType.objects.all()
    return qs


@api.get("/accounts", response=List[AccountOut])
def list_accounts(request):
    qs = Account.objects.all()
    return qs


@api.get("/tags", response=List[TagOut])
def list_tags(request):
    qs = Tag.objects.all()
    return qs


@api.put("/accounts/types/{accounttype_id}")
def update_account_type(request, accounttype_id: int, payload: AccountTypeIn):
    account_type = get_object_or_404(AccountType, id=accounttype_id)
    account_type.account_type = payload.account_type
    account_type.color = payload.color
    account_type.icon = payload.icon
    account_type.save()
    return {"success": True}


@api.put("/accounts/{account_id}")
def update_account(request, account_id: int, payload: AccountIn):
    account = get_object_or_404(Account, id=account_id)
    account.account_name = payload.account_name
    account.account_type = payload.account_type
    account.opening_balance = payload.opening_balance
    account.apy = payload.apy
    account.due_date = payload.due_date
    account.active = payload.active
    account.open_date = payload.open_date
    account.next_cycle_date = payload.next_cycle_date
    account.statement_cycle_length = payload.statement_cycle_length
    account.rewards_amount = payload.rewards_amount
    account.save()
    return {"sucess": True}


@api.put("/tags/{tag_id}")
def update_tag(request, tag_id: int, payload: TagIn):
    tag = get_object_or_404(Tag, id=tag_id)
    tag.tag_name = payload.tag_name
    tag.parent_id = payload.parent_id
    tag.save()
    return {"sucess": True}


@api.delete("/accounts/types/{accounttype_id}")
def delete_account_type(request, accounttype_id: int):
    account_type = get_object_or_404(AccountType, id=accounttype_id)
    account_type.delete()
    return {"success": True}


@api.delete("/accounts/{account_id}")
def delete_account(request, account_id: int):
    account = get_object_or_404(Account, id=account_id)
    account.delete()
    return {"success": True}


@api.delete("/tags/{tag_id}")
def delete_tag(request, tag_id: int):
    tag = get_object_or_404(Tag, id=tag_id)
    tag.delete()
    return {"success": True}
