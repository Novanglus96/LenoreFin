from ninja import NinjaAPI, Schema, Query
from api.models import Account, AccountType, CalendarDate, Tag, ChristmasGift, ContribRule, Contribution, ErrorLevel, TransactionType, Repeat, Reminder, Note, Option, TransactionStatus, Transaction, TransactionDetail, LogEntry, Payee, TagType, Bank, Paycheck
from typing import List, Optional
from django.shortcuts import get_object_or_404
from decimal import Decimal
from datetime import date, timedelta
from pydantic import BaseModel, Field
from ninja.security import HttpBearer
from decouple import config
from django.db.models import Case, When, Q
from django.db import models


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


class BankIn(Schema):
    bank_name: str


class BankOut(Schema):
    id: int
    bank_name: str


class AccountIn(Schema):
    account_name: str
    account_type_id: int
    opening_balance: Optional[Decimal] = Field(whole_digits=10, decimal_places=2)
    apy: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)
    due_date: Optional[date]
    active: bool
    open_date: Optional[date]
    next_cycle_date: Optional[date]
    statement_cycle_length: Optional[int]
    statement_cycle_period: Optional[str]
    rewards_amount: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)
    credit_limit: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)
    bank_id: int
    last_statement_amount: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)


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
    available_credit: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)
    balance: Optional[Decimal] = Field(whole_digits=10, decimal_places=2)
    bank: BankOut
    last_statement_amount: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)


class TagTypeIn(Schema):
    tag_type: str


class TagTypeOut(Schema):
    id: int
    tag_type: str


class TagIn(Schema):
    tag_name: str
    parent_id: Optional[int] = None
    tag_type_id: Optional[int] = None


class TagOut(Schema):
    id: int
    tag_name: str
    parent: Optional['TagOut'] = None
    tag_type: Optional[TagTypeOut] = None


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


class PayeeIn(Schema):
    payee_name: str


class PayeeOut(Schema):
    id: int
    payee_name: str


class PaycheckIn(Schema):
    gross: Decimal = Field(whole_digits=10, decimal_places=2)
    net: Decimal = Field(whole_digits=10, decimal_places=2)
    taxes: Decimal = Field(whole_digits=10, decimal_places=2)
    health: Decimal = Field(whole_digits=10, decimal_places=2)
    pension: Decimal = Field(whole_digits=10, decimal_places=2)
    fsa: Decimal = Field(whole_digits=10, decimal_places=2)
    dca: Decimal = Field(whole_digits=10, decimal_places=2)
    union_dues: Decimal = Field(whole_digits=10, decimal_places=2)
    four_fifty_seven_b: Decimal = Field(whole_digits=10, decimal_places=2)
    payee_id: int


class PaycheckOut(Schema):
    id: int
    gross: Decimal = Field(whole_digits=10, decimal_places=2)
    net: Decimal = Field(whole_digits=10, decimal_places=2)
    taxes: Decimal = Field(whole_digits=10, decimal_places=2)
    health: Decimal = Field(whole_digits=10, decimal_places=2)
    pension: Decimal = Field(whole_digits=10, decimal_places=2)
    fsa: Decimal = Field(whole_digits=10, decimal_places=2)
    dca: Decimal = Field(whole_digits=10, decimal_places=2)
    union_dues: Decimal = Field(whole_digits=10, decimal_places=2)
    four_fifty_seven_b: Decimal = Field(whole_digits=10, decimal_places=2)
    payee: PayeeOut


class TransactionIn(Schema):
    transaction_date: date
    total_amount: Decimal = Field(whole_digits=10, decimal_places=2)
    status_id: int
    memo: str
    description: str
    edit_date: date
    add_date: date
    transaction_type_id: int
    reminder_id: Optional[int] = None
    paycheck_id: Optional[int] = None


class TransactionClear(Schema):
    status_id: int
    edit_date: date


class TransactionDetailOut(Schema):
    id: int
    transaction: 'TransactionOut'
    account: AccountOut
    detail_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    tag: TagOut


class TransactionOut(Schema):
    id: int
    transaction_date: date
    total_amount: Decimal = Field(whole_digits=10, decimal_places=2)
    status: TransactionStatusOut
    memo: str
    description: str
    edit_date: date
    add_date: date
    transaction_type: TransactionTypeOut
    reminder: Optional[ReminderOut] = None
    paycheck: Optional[PaycheckOut] = None
    balance: Optional[Decimal] = Field(default=None, whole_digits=10, decimal_places=2)
    pretty_account: Optional[str]
    tags: Optional[List[str]]
    details: List[TransactionDetailOut] = []
    pretty_total: Optional[Decimal] = Field(default=None, whole_digits=10, decimal_places=2)


TransactionDetailOut.update_forward_refs()


class TransactionDetailIn(Schema):
    transaction_id: int
    account_id: int
    detail_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    tag_id: int


class LogEntryIn(Schema):
    log_date: date
    log_entry: str
    account_id: Optional[int] = None
    reminder_id: Optional[int] = None
    transaction_id: Optional[int] = None
    error_num: Optional[int] = None
    error_level_id: Optional[int] = None


class LogEntryOut(Schema):
    log_date: date
    log_entry: str
    account: Optional[AccountOut] = None
    reminder: Optional[ReminderOut] = None
    transaction: Optional[TransactionOut] = None
    error_num: Optional[int] = None
    error_level: Optional[ErrorLevelOut] = None


@api.post("/accounts/types")
def create_account_type(request, payload: AccountTypeIn):
    account_type = AccountType.objects.create(**payload.dict())
    return {"id": account_type.id}


@api.post("/accounts/banks")
def create_bank(request, payload: BankIn):
    bank = Bank.objects.create(**payload.dict())
    return {"id": bank.id}


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


@api.post("/payees")
def create_payee(request, payload: PayeeIn):
    payee = Payee.objects.create(**payload.dict())
    return {"id": payee.id}


@api.post("/paychecks")
def create_paycheck(request, payload: PaycheckIn):
    paycheck = Paycheck.objects.create(**payload.dict())
    return {"id": paycheck.id}


@api.post("/transactions")
def create_transaction(request, payload: TransactionIn):
    transaction = Transaction.objects.create(**payload.dict())
    return {"id": transaction.id}


@api.post("/transactions/details")
def create_transaction_detail(request, payload: TransactionDetailIn):
    transaction_detail = TransactionDetail.objects.create(**payload.dict())
    return {"id": transaction_detail.id}


@api.post("/logentries")
def create_log_entry(request, payload: LogEntryIn):
    log_entry = LogEntry.objects.create(**payload.dict())
    return {"id": log_entry.id}


@api.get("/accounts/types/{accounttype_id}", response=AccountTypeOut)
def get_account_type(request, accounttype_id: int):
    account_type = get_object_or_404(AccountType, id=accounttype_id)
    return account_type


@api.get("/accounts/banks/{bank_id}", response=BankOut)
def get_bank(request, bank_id: int):
    bank = get_object_or_404(Bank, id=bank_id)
    return bank


@api.get("/accounts/{account_id}", response=AccountOut)
def get_account(request, account_id: int):
    account = get_object_or_404(Account, id=account_id)
    transactions = Transaction.objects.exclude(status_id=1)
    transactions = TransactionDetail.objects.filter(account__id=account_id).exclude(transaction__status__id=1)
    calc_balance = account.opening_balance
    for transaction in transactions:
        calc_balance += transaction.detail_amt
    account_out = AccountOut(
        id=account.id,
        account_name=account.account_name,
        account_type=AccountTypeOut(id=account.account_type.id, account_type=account.account_type.account_type, color=account.account_type.color, icon=account.account_type.icon),
        opening_balance=account.opening_balance,
        apy=account.apy,
        due_date=account.due_date,
        active=account.active,
        open_date=account.open_date,
        next_cycle_date=account.next_cycle_date,
        statement_cycle_length=account.statement_cycle_length,
        statement_cycle_period=account.statement_cycle_period,
        rewards_amount=account.rewards_amount,
        credit_limit=account.credit_limit,
        available_credit=account.credit_limit + calc_balance,
        balance=calc_balance,
        bank=BankOut(id=account.bank.id, bank_name=account.bank.bank_name),
        last_statement_amount=account.last_statement_amount
    )
    return account_out


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


@api.get("/payees/{payee_id}", response=PayeeOut)
def get_payee(request, payee_id: int):
    payee = get_object_or_404(Payee, id=payee_id)
    return payee


@api.get("/paychecks/{paycheck_id}", response=PaycheckOut)
def get_paycheck(request, paycheck_id: int):
    paycheck = get_object_or_404(Paycheck, id=paycheck_id)
    return paycheck


@api.get("/transactions/{transaction_id}", response=TransactionOut)
def get_transaction(request, transaction_id: int):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    return transaction


@api.get("/transactions/details/{transactiondetail_id}", response=TransactionDetailOut)
def get_transaction_detail(request, transactiondetail_id: int):
    transaction_detail = get_object_or_404(TransactionDetail, id=transactiondetail_id)
    return transaction_detail


@api.get("/logentries/{logentry_id}", response=LogEntryOut)
def get_log_entry(request, logentry_id: int):
    log_entry = get_object_or_404(LogEntry, id=logentry_id)
    return log_entry


@api.get("/accounts/types", response=List[AccountTypeOut])
def list_account_types(request):
    qs = AccountType.objects.all().order_by('id')
    return qs


@api.get("/accounts/banks", response=List[BankOut])
def list_banks(request):
    qs = Bank.objects.all().order_by('bank_name')
    return qs


@api.get("/accounts", response=List[AccountOut])
def list_accounts(request, account_type: Optional[int] = Query(None)):
    qs = Account.objects.all()

    if account_type is not None:
        qs = qs.filter(account_type__id=account_type)
    qs = qs.order_by('account_type__id', 'account_name')

    account_list = []
    for account in qs:
        calc_balance = account.opening_balance
        transactions = TransactionDetail.objects.filter(account__id=account.id).exclude(transaction__status__id=1)
        for transaction in transactions:
            calc_balance += transaction.detail_amt
        account_out = AccountOut(
            id=account.id,
            account_name=account.account_name,
            account_type=AccountTypeOut(id=account.account_type.id, account_type=account.account_type.account_type, color=account.account_type.color, icon=account.account_type.icon),
            opening_balance=account.opening_balance,
            apy=account.apy,
            due_date=account.due_date,
            active=account.active,
            open_date=account.open_date,
            next_cycle_date=account.next_cycle_date,
            statement_cycle_length=account.statement_cycle_length,
            statement_cycle_period=account.statement_cycle_period,
            rewards_amount=account.rewards_amount,
            credit_limit=account.credit_limit,
            available_credit=account.credit_limit + calc_balance,
            balance=calc_balance,
            bank=BankOut(id=account.bank.id, bank_name=account.bank.bank_name),
            last_statement_amount=account.last_statement_amount
        )
        account_list.append(account_out)

    return account_list


@api.get("/tags", response=List[TagOut])
def list_tags(request, tag_type: Optional[int] = Query(None)):
    qs = Tag.objects.all()

    if tag_type is not None:
        qs = qs.filter(tag_type__id=tag_type)

    qs = qs.order_by('parent__tag_name', 'tag_name')
    return qs


@api.get("/planning/contribrules", response=List[ContribRuleOut])
def list_contrib_rules(request):
    qs = ContribRule.objects.all().order_by('id')
    return qs


@api.get("/planning/contributions", response=List[ContributionOut])
def list_contributions(request):
    qs = Contribution.objects.all().order_by('id')
    return qs


@api.get("/errorlevels", response=List[ErrorLevelOut])
def list_errorlevels(request):
    qs = ErrorLevel.objects.all().order_by('id')
    return qs


@api.get("/transactions/types", response=List[TransactionTypeOut])
def list_transaction_types(request):
    qs = TransactionType.objects.all().order_by('id')
    return qs


@api.get("/reminders/repeats", response=List[RepeatOut])
def list_repeats(request):
    qs = Repeat.objects.all().order_by('id')
    return qs


@api.get("/reminders", response=List[ReminderOut])
def list_reminders(request):
    qs = Reminder.objects.all().order_by('id')
    return qs


@api.get("/planning/notes", response=List[NoteOut])
def list_notes(request):
    qs = Note.objects.all().order_by('-note_date')
    return qs


@api.get("/options", response=List[OptionOut])
def list_options(request):
    qs = Option.objects.all().order_by('id')
    return qs


@api.get("/transactions/statuses", response=List[TransactionStatusOut])
def list_transaction_statuses(request):
    qs = TransactionStatus.objects.all().order_by('id')
    return qs


@api.get("/payees", response=List[PayeeOut])
def list_payees(request):
    qs = Payee.objects.all().order_by('payee_name')
    return qs


@api.get("/paychecks", response=List[PaycheckOut])
def list_paychecks(request):
    qs = Paycheck.objects.all().order_by('id')
    return qs


@api.get("/transactions", response=List[TransactionOut])
def list_transactions(request, account: Optional[int] = Query(None), maxdays: Optional[int] = Query(14)):
    qs = Transaction.objects.all()

    if account is not None:
        threshold_date = date.today() + timedelta(days=maxdays)
        qs = qs.filter(
            transactiondetail__account__id=account,
            transaction_date__lt=threshold_date
        )
        custom_order = Case(
            When(status_id=3, then=0),
            When(status_id=2, then=0),
            When(status_id=1, then=1),
            output_field=models.IntegerField(),
        )
        qs = qs.order_by(custom_order, 'transaction_date', '-id')
        transactions = []
        balance = Decimal(0)  # Initialize the balance
        for transaction in qs:
            pretty_account = ''
            tags = []
            pretty_total = 0
            source_account = ''
            destination_account = ''
            transaction_details = TransactionDetail.objects.filter(transaction=transaction.id)
            for detail in transaction_details:
                if detail.tag.tag_name not in tags:
                    tags.append(detail.tag.tag_name)
                if transaction.transaction_type.id == 3:
                    if detail.detail_amt < 0:
                        source_account = detail.account.account_name
                        if detail.account.id == account:
                            pretty_total = transaction.total_amount
                    else:
                        destination_account = detail.account.account_name
                        if detail.account.id == account:
                            pretty_total = -transaction.total_amount
                    if detail.account.id == account:
                        balance += detail.detail_amt
                else:
                    pretty_total = transaction.total_amount
                    source_account = detail.account.account_name
                    balance += transaction.total_amount
            if transaction.transaction_type.id == 3:
                pretty_account = source_account + ' => ' + destination_account
            else:
                pretty_account = source_account

            # Update the balance in the transaction and append to the list
            transaction.balance = balance
            transaction.pretty_account = pretty_account
            transaction.tags = tags
            transaction.pretty_total = pretty_total
            transactions.append(TransactionOut.from_orm(transaction))
        transactions.reverse()
        return transactions
    else:
        qs = qs.filter(status_id=1)
        custom_order = Case(
            When(status_id=1, then=0),
            When(status_id=2, then=1),
            When(status_id=3, then=1),
            output_field=models.IntegerField(),
        )
        qs = qs.order_by(custom_order, 'transaction_date', 'id')
        for transaction in qs:
            tags = []
            source_account = ''
            destination_account = ''
            pretty_account = ''
            transaction_details = TransactionDetail.objects.filter(transaction=transaction.id)
            for detail in transaction_details:
                if detail.tag.tag_name not in tags:
                    tags.append(detail.tag.tag_name)
                if transaction.transaction_type.id == 3:
                    if detail.detail_amt < 0:
                        source_account = detail.account.account_name
                    else:
                        destination_account = detail.account.account_name
                    pretty_account = source_account + ' => ' + destination_account
                else:
                    pretty_account = detail.account.account_name
            transaction.tags = tags
            transaction.pretty_account = pretty_account
            transaction.pretty_total = transaction.total_amount

        return qs


@api.get("/transactions/details", response=List[TransactionDetailOut])
def list_transactiondetails(request):
    qs = TransactionDetail.objects.all().order_by('id')
    return qs


@api.get("/logentries", response=List[LogEntryOut])
def list_log_entries(request):
    qs = LogEntry.objects.all().order_by('-log_date')
    return qs


@api.put("/accounts/types/{accounttype_id}")
def update_account_type(request, accounttype_id: int, payload: AccountTypeIn):
    account_type = get_object_or_404(AccountType, id=accounttype_id)
    account_type.account_type = payload.account_type
    account_type.color = payload.color
    account_type.icon = payload.icon
    account_type.save()
    return {"success": True}


@api.put("/accounts/banks/{bank_id}")
def update_bank(request, bank_id: int, payload: BankIn):
    bank = get_object_or_404(Bank, id=bank_id)
    bank.bank_name = payload.bank_name
    bank.save()
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
    account.statement_cycle_period = payload.statement_cycle_period
    account.rewards_amount = payload.rewards_amount
    account.credit_limit = payload.credit_limit
    account.bank_id = payload.bank_id
    account.last_statement_amount = payload.last_statement_amount
    account.save()
    return {"success": True}


@api.put("/tags/{tag_id}")
def update_tag(request, tag_id: int, payload: TagIn):
    tag = get_object_or_404(Tag, id=tag_id)
    tag.tag_name = payload.tag_name
    tag.parent_id = payload.parent_id
    tag.tag_type_id = payload.tag_type_id
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
def update_transaction_status(request, transactionstatus_id: int, payload: TransactionStatusIn):
    transaction_status = get_object_or_404(TransactionStatus, id=transactionstatus_id)
    transaction_status.transaction_status = payload.transaction_status
    transaction_status.save()
    return {"success": True}


@api.put("/payees/{payee_id}")
def update_payee(request, payee_id: int, payload: PayeeIn):
    payee = get_object_or_404(Payee, id=payee_id)
    payee.payee_name = payload.payee_name
    payee.save()
    return {"success": True}


@api.put("/paychecks/{paycheck_id}")
def update_paycheck(request, paycheck_id: int, payload: PaycheckIn):
    paycheck = get_object_or_404(Paycheck, id=paycheck_id)
    paycheck.gross = payload.gross
    paycheck.net = payload.net
    paycheck.taxes = payload.taxes
    paycheck.health = payload.health
    paycheck.pension = payload.pension
    paycheck.fsa = payload.fsa
    paycheck.dca = payload.dca
    paycheck.union_dues = payload.union_dues
    paycheck.four_fifty_seven_b = payload.four_fifty_seven_b
    paycheck.payee_id = payload.payee_id
    paycheck.save()
    return {"success": True}


@api.put("/transactions/{transaction_id}")
def update_transaction(request, transaction_id: int, payload: TransactionIn):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.transaction_date = payload.transaction_date
    transaction.total_amount = payload.total_amount
    transaction.status_id = payload.status_id
    transaction.memo = payload.memo
    transaction.description = payload.description
    transaction.edit_date = payload.edit_date
    transaction.add_date = payload.add_date
    transaction.transaction_type_id = payload.transaction_type_id
    transaction.reminder_id = payload.reminder_id
    transaction.paycheck_id = payload.paycheck_id
    transaction.save()
    return {"success": True}


@api.patch("/transactions/clear/{transaction_id}")
def clear_transaction(request, transaction_id: int, payload: TransactionClear):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.status_id = payload.status_id
    transaction.edit_date = payload.edit_date
    transaction.save()
    return {"success": True}


@api.put("/transactions/details/{transactiondetail_id}")
def update_transaction_detail(request, transactiondetail_id: int, payload: TransactionDetailIn):
    transaction_detail = get_object_or_404(TransactionDetail, id=transactiondetail_id)
    transaction_detail.transaction_id = payload.transaction_id
    transaction_detail.account_id = payload.account_id
    transaction_detail.detail_amt = payload.detail_amt
    transaction_detail.tag_id = payload.tag_id
    transaction_detail.save()
    return {"success": True}


@api.put("/logentries/{logentry_id}")
def update_log_entry(request, logentry_id: int, payload: LogEntryIn):
    log_entry = get_object_or_404(LogEntry, id=logentry_id)
    log_entry.log_date = payload.log_date
    log_entry.log_entry = payload.log_entry
    log_entry.account_id = payload.account_id
    log_entry.reminder_id = payload.reminder_id
    log_entry.transaction_id = payload.transaction_id
    log_entry.error_num = payload.error_num
    log_entry.error_level_id = payload.error_level_id
    log_entry.save()
    return {"success": True}


@api.delete("/accounts/types/{accounttype_id}")
def delete_account_type(request, accounttype_id: int):
    account_type = get_object_or_404(AccountType, id=accounttype_id)
    account_type.delete()
    return {"success": True}


@api.delete("/accounts/banks/{bank_id}")
def delete_bank(request, bank_id: int):
    bank = get_object_or_404(Bank, id=bank_id)
    bank.delete()
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


@api.delete("/payees/{payee_id}")
def delete_payee(request, payee_id: int):
    payee = get_object_or_404(Payee, id=payee_id)
    payee.delete()
    return {"success": True}


@api.delete("/paychecks/{paycheck_id}")
def delete_paycheck(request, paycheck_id: int):
    paycheck = get_object_or_404(Paycheck, id=paycheck_id)
    paycheck.delete()
    return {"success": True}


@api.delete("/transactions/{transaction_id}")
def delete_transaction(request, transaction_id: int):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.delete()
    return {"success": True}


@api.delete("/transactions/details/{transactiondetail_id}")
def delete_transaction_detail(request, transactiondetail_id: int):
    transaction_detail = get_object_or_404(TransactionDetail, id=transactiondetail_id)
    transaction_detail.delete()
    return {"success": True}


@api.delete("/logentries/{logentry_id}")
def delete_log_entry(request, logentry_id: int):
    log_entry = get_object_or_404(LogEntry, id=logentry_id)
    log_entry.delete()
    return {"success": True}
