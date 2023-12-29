from ninja import NinjaAPI, Schema
from api.models import Account, AccountType, CalendarDate, Tag, ChristmasGift, ContribRule, Contribution, ErrorLevel, TransactionType, Repeat, Reminder, Note, Option, TransactionStatus, Transaction, TransactionDetail, LogEntry
from typing import List, Optional
from django.shortcuts import get_object_or_404
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field
from ninja.security import HttpBearer
from decouple import config


class GlobalAuth(HttpBearer):
    def authenticate(self, request, token):
        api_key = config("API_KEY", default=None)
        if token == api_key:
            return token


api = NinjaAPI(auth=GlobalAuth())
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
    account_type_id: int
    opening_balance: Decimal = Field(whole_digits=10, decimal_places=2)
    apy: Decimal = Field(whole_digits=2, decimal_places=2)
    due_date: Optional[date]
    active: bool
    open_date: date
    next_cycle_date: Optional[date]
    statement_cycle_length: Optional[int]
    rewards_amount: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)


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
    rewards_amount: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)


class TagIn(Schema):
    tag_name: str
    parent_id: Optional[int] = None


class TagOut(Schema):
    id: int
    tag_name: str
    parent_id: Optional[int] = None


class ContribRuleIn(Schema):
    rule: str
    cap: Optional[str] = None


class ContribRuleOut(Schema):
    id: int
    rule: str
    cap: Optional[str] = None


class ContributionIn(Schema):
    contribution: str
    per_paycheck: Decimal = Field(whole_digits=10, decimal_places=2)
    emergency_diff: Decimal = Field(whole_digits=10, decimal_places=2)
    emergency_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    cap: Decimal = Field(whole_digits=10, decimal_places=2)
    active: bool


class ContributionOut(Schema):
    id: int
    contribution: str
    per_paycheck: Decimal = Field(whole_digits=10, decimal_places=2)
    emergency_diff: Decimal = Field(whole_digits=10, decimal_places=2)
    emergency_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    cap: Decimal = Field(whole_digits=10, decimal_places=2)
    active: bool


class ErrorLevelIn(Schema):
    error_level: str


class ErrorLevelOut(Schema):
    id: int
    error_level: str


class TransactionTypeIn(Schema):
    transaction_type: str


class TransactionTypeOut(Schema):
    id: int
    transaction_type: str


class RepeatIn(Schema):
    repeat_name: str
    days: Optional[int] = 0
    weeks: Optional[int] = 0
    months: Optional[int] = 0
    years: Optional[int] = 0


class RepeatOut(Schema):
    id: int
    repeat_name: str
    days: Optional[int] = 0
    weeks: Optional[int] = 0
    months: Optional[int] = 0
    years: Optional[int] = 0


class ReminderIn(Schema):
    tag_id: int
    amount: Decimal = Field(whole_digits=10, decimal_places=2)
    reminder_source_account_id: int
    reminder_destination_account_id: Optional[int]
    description: str
    transaction_type_id: int
    start_date: date
    end_date: date
    repeat_id: int
    auto_add: bool


class ReminderOut(Schema):
    id: int
    tag: TagOut
    amount: Decimal = Field(whole_digits=10, decimal_places=2)
    reminder_source_account: AccountOut
    reminder_destination_account: Optional[AccountOut]
    description: str
    transaction_type: TransactionTypeOut
    start_date: date
    end_date: date
    repeat: RepeatOut
    auto_add: bool


class NoteIn(Schema):
    note_text: str
    note_date: date


class NoteOut(Schema):
    id: int
    note_text: str
    note_date: date


class OptionIn(Schema):
    log_level_id: int
    alert_balance: Decimal = Field(whole_digits=10, decimal_places=2)
    alert_period: int


class OptionOut(Schema):
    id: int
    log_level: ErrorLevelOut
    alert_balance: Decimal = Field(whole_digits=10, decimal_places=2)
    alert_period: int


class TransactionStatusIn(Schema):
    transaction_status: str


class TransactionStatusOut(Schema):
    id: int
    transaction_status: str


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


@api.post("/planning/contribrules")
def create_contrib_rule(request, payload: ContribRuleIn):
    contrib_rule = ContribRule.objects.create(**payload.dict())
    return {"id": contrib_rule.id}


@api.post("/planning/contributions")
def create_contribution(request, payload: ContributionIn):
    contribution = Contribution.objects.create(**payload.dict())
    return {"id": contribution.id}


@api.post("/errorlevels")
def create_errorlevel(request, payload: ErrorLevelIn):
    errorlevel = ErrorLevel.objects.create(**payload.dict())
    return {"id": errorlevel.id}


@api.post("/transactions/types")
def create_transaction_type(request, payload: TransactionTypeIn):
    transaction_type = TransactionType.objects.create(**payload.dict())
    return {"id": transaction_type.id}


@api.post("/reminders/repeats")
def create_repeat(request, payload: RepeatIn):
    repeat = Repeat.objects.create(**payload.dict())
    return {"id": repeat.id}


@api.post("/reminders")
def create_reminder(request, payload: ReminderIn):
    reminder = Reminder.objects.create(**payload.dict())
    return {"id": reminder.id}


@api.post("/planning/notes")
def create_note(request, payload: NoteIn):
    note = Note.objects.create(**payload.dict())
    return {"id": note.id}


@api.post("/options")
def create_option(request, payload: OptionIn):
    option = Option.objects.create(**payload.dict())
    return {"id": option.id}


@api.post("/transactions/statuses")
def create_transaction_status(request, payload: TransactionStatusIn):
    transaction_status = TransactionStatus.objects.create(**payload.dict())
    return {"id": transaction_status.id}


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


@api.get("/planning/contribrules/{contribrule_id}", response=ContribRuleOut)
def get_contribrule(request, contribrule_id: int):
    contrib_rule = get_object_or_404(ContribRule, id=contribrule_id)
    return contrib_rule


@api.get("/planning/contributions/{contribution_id}", response=ContributionOut)
def get_contribution(request, contribution_id: int):
    contribution = get_object_or_404(Contribution, id=contribution_id)
    return contribution


@api.get("/errorlevels/{errorlevel_id}", response=ErrorLevelOut)
def get_errorlevel(request, errorlevel_id: int):
    errorlevel = get_object_or_404(ErrorLevel, id=errorlevel_id)
    return errorlevel


@api.get("/transactions/types/{transaction_type_id}", response=TransactionTypeOut)
def get_transaction_type(request, transaction_type_id: int):
    transaction_type = get_object_or_404(TransactionType, id=transaction_type_id)
    return transaction_type


@api.get("/reminders/repeats/{repeat_id}", response=RepeatOut)
def get_repeat(request, repeat_id: int):
    repeat = get_object_or_404(Repeat, id=repeat_id)
    return repeat


@api.get("/reminders/{reminder_id}", response=ReminderOut)
def get_reminder(request, reminder_id: int):
    reminder = get_object_or_404(Reminder, id=reminder_id)
    return reminder


@api.get("/planning/notes/{note_id}", response=NoteOut)
def get_note(request, note_id: int):
    note = get_object_or_404(Note, id=note_id)
    return note


@api.get("/options/{option_id}", response=OptionOut)
def get_option(request, option_id: int):
    option = get_object_or_404(Option, id=option_id)
    return option


@api.get("/transactions/statuses/{transactionstatus_id}", response=TransactionStatusOut)
def get_transaction_status(request, transactionstatus_id: int):
    transaction_status = get_object_or_404(TransactionStatus, id=transactionstatus_id)
    return transaction_status


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


@api.get("/planning/contribrules", response=List[ContribRuleOut])
def list_contrib_rules(request):
    qs = ContribRule.objects.all()
    return qs


@api.get("/planning/contributions", response=List[ContributionOut])
def list_contributions(request):
    qs = Contribution.objects.all()
    return qs


@api.get("/errorlevels", response=List[ErrorLevelOut])
def list_errorlevels(request):
    qs = ErrorLevel.objects.all()
    return qs


@api.get("/transactions/types", response=List[TransactionTypeOut])
def list_transaction_types(request):
    qs = TransactionType.objects.all()
    return qs


@api.get("/reminders/repeats", response=List[RepeatOut])
def list_repeats(request):
    qs = Repeat.objects.all()
    return qs


@api.get("/reminders", response=List[ReminderOut])
def list_reminders(request):
    qs = Reminder.objects.all()
    return qs


@api.get("/planning/notes", response=List[NoteOut])
def list_notes(request):
    qs = Note.objects.all()
    return qs


@api.get("/options", response=List[OptionOut])
def list_options(request):
    qs = Option.objects.all()
    return qs


@api.get("/transactions/statuses", response=List[TransactionStatusOut])
def list_transaction_statuses(request):
    qs = TransactionStatus.objects.all()
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
    account.account_type_id = payload.account_type_id
    account.opening_balance = payload.opening_balance
    account.apy = payload.apy
    account.due_date = payload.due_date
    account.active = payload.active
    account.open_date = payload.open_date
    account.next_cycle_date = payload.next_cycle_date
    account.statement_cycle_length = payload.statement_cycle_length
    account.rewards_amount = payload.rewards_amount
    account.save()
    return {"success": True}


@api.put("/tags/{tag_id}")
def update_tag(request, tag_id: int, payload: TagIn):
    tag = get_object_or_404(Tag, id=tag_id)
    tag.tag_name = payload.tag_name
    tag.parent_id = payload.parent_id
    tag.save()
    return {"success": True}


@api.put("/planning/contribrules/{contribrule_id}")
def update_contrib_rule(request, contribrule_id: int, payload: ContribRuleIn):
    contrib_rule = get_object_or_404(ContribRule, id=contribrule_id)
    contrib_rule.rule = payload.rule
    contrib_rule.cap = payload.cap
    contrib_rule.save()
    return {"success": True}


@api.put("/planning/contributions/{contribution_id}")
def update_contribution(request, contribution_id: int, payload: ContributionIn):
    contribution = get_object_or_404(Contribution, id=contribution_id)
    contribution.contribution = payload.contribution
    contribution.per_paycheck = payload.per_paycheck
    contribution.emergency_amt = payload.emergency_amt
    contribution.emergency_diff = payload.emergency_diff
    contribution.cap = payload.cap
    contribution.active = payload.active
    contribution.save()
    return {"success": True}


@api.put("/errorlevels/{errorlevel_id}")
def update_errorlevel(request, errorlevel_id: int, payload: ErrorLevelIn):
    errorlevel = get_object_or_404(ErrorLevel, id=errorlevel_id)
    errorlevel.error_level = payload.error_level
    errorlevel.save()
    return {"success": True}


@api.put("/transactions/types/{transaction_type_id}")
def update_transaction_type(request, transaction_type_id: int, payload: TransactionTypeIn):
    transaction_type = get_object_or_404(TransactionType, id=transaction_type_id)
    transaction_type.transaction_type = payload.transaction_type
    transaction_type.save()
    return {"success": True}


@api.put("/reminders/repeats/{repeat_id}")
def update_repeat(request, repeat_id: int, payload: RepeatIn):
    repeat = get_object_or_404(Repeat, id=repeat_id)
    repeat.repeat_name = payload.repeat_name
    repeat.days = payload.days
    repeat.weeks = payload.weeks
    repeat.months = payload.months
    repeat.years = payload.years
    repeat.save()
    return {"success": True}


@api.put("/reminders/{reminder_id}")
def update_reminder(request, reminder_id: int, payload: ReminderIn):
    reminder = get_object_or_404(Reminder, id=reminder_id)
    reminder.tag_id = payload.tag_id
    reminder.amount = payload.amount
    reminder.reminder_source_account_id = payload.reminder_source_account_id
    reminder.reminder_destination_account_id = payload.reminder_destination_account_id
    reminder.description = payload.description
    reminder.transaction_type_id = payload.transaction_type_id
    reminder.start_date = payload.start_date
    reminder.end_date = payload.end_date
    reminder.repeat_id = payload.repeat_id
    reminder.auto_add = payload.auto_add
    reminder.save()
    return {"success": True}


@api.put("/planning/notes/{note_id}")
def update_note(request, note_id: int, payload: NoteIn):
    note = get_object_or_404(Note, id=note_id)
    note.note_text = payload.note_text
    note.note_date = payload.note_date
    note.save()
    return {"success": True}


@api.put("/options/{option_id}")
def update_option(request, option_id: int, payload: OptionIn):
    option = get_object_or_404(Option, id=option_id)
    option.log_level_id = payload.log_level_id
    option.alert_balance = payload.alert_balance
    option.alert_period = payload.alert_period
    option.save()
    return {"success": True}


@api.put("/transactions/statuses/{transactionstatus_id}")
def update_transaction_status(request, transationstatus_id: int, payload: TransactionStatusIn):
    transaction_status = get_object_or_404(TransactionStatus, id=transationstatus_id)
    transaction_status.transaction_status = payload.transaction_status
    transaction_status.save()
    return {"success": True}


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


@api.delete("/planning/contribrules/{contribrule_id}")
def delete_contrib_rule(request, contribrule_id: int):
    contrib_rule = get_object_or_404(ContribRule, id=contribrule_id)
    contrib_rule.delete()
    return {"success": True}


@api.delete("/planning/contributions/{contribution_id}")
def delete_contribution(request, contribution_id: int):
    contribution = get_object_or_404(Contribution, id=contribution_id)
    contribution.delete()
    return {"success": True}


@api.delete("/errorlevels/{errorlevel_id}")
def delete_errorlevel(request, errorlevel_id: int):
    errorlevel = get_object_or_404(ErrorLevel, id=errorlevel_id)
    errorlevel.delete()
    return {"success": True}


@api.delete("/transactions/types/{transaction_type_id}")
def delete_transaction_type(request, transaction_type_id: int):
    transaction_type = get_object_or_404(TransactionType, id=transaction_type_id)
    transaction_type.delete()
    return {"success": True}


@api.delete("/reminders/repeats/{repeat_id}")
def delete_repeat(request, repeat_id: int):
    repeat = get_object_or_404(Repeat, id=repeat_id)
    repeat.delete()
    return {"success": True}


@api.delete("/reminders/{reminder_id}")
def delete_reminder(request, reminder_id: int):
    reminder = get_object_or_404(Reminder, id=reminder_id)
    reminder.delete()
    return {"success": True}


@api.delete("/planning/notes/{note_id}")
def delete_note(request, note_id: int):
    note = get_object_or_404(Note, id=note_id)
    note.delete()
    return {"success": True}


@api.delete("/options/{option_id}")
def delete_option(request, option_id: int):
    option = get_object_or_404(Option, id=option_id)
    option.delete()
    return {"success": True}


@api.delete("/transactions/statuses/{transactionstatus_id}")
def delete_transaction_status(request, transactionstatus_id: int):
    transaction_status = get_object_or_404(TransactionStatus, id=transactionstatus_id)
    transaction_status.delete()
    return {"success": True}
