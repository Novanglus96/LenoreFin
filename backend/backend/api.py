"""
Module: api.py
Description: Contains django-ninja api schemas and definitions.

Author: John Adams <johnmadams96@gmail.com>
Date: February 13, 2024
"""

from ninja import NinjaAPI, Schema, Query, File
from ninja.files import UploadedFile
from transactions.models import (
    TransactionType,
    TransactionStatus,
    Transaction,
    TransactionDetail,
    Paycheck,
    sort_transactions,
    create_transactions,
    CustomTag,
    FullTransaction,
)
from imports.models import (
    FileImport,
    TransactionImport,
    TransactionImportTag,
    TransactionImportError,
    TypeMapping,
    StatusMapping,
    AccountMapping,
    TagMapping,
)
from accounts.models import AccountType, Bank, Account
from tags.models import Tag, TagType
from reminders.models import Repeat, Reminder
from planning.models import ChristmasGift, ContribRule, Contribution, Note
from administration.models import (
    ErrorLevel,
    LogEntry,
    Message,
    Option,
    Payee,
    logToDB,
)
from typing import List, Optional
from django.shortcuts import get_object_or_404
from decimal import Decimal
from datetime import date, timedelta, datetime
from pydantic import BaseModel, Field
from ninja.security import HttpBearer
from ninja.errors import HttpError
from decouple import config
from django.db.models import (
    Case,
    When,
    Q,
    IntegerField,
    Value,
    F,
    CharField,
    Sum,
)
from django.db import models, IntegrityError
from django.db.models.functions import Concat
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import random
import json
from django.core.paginator import Paginator
from django.db.models.signals import pre_delete, post_delete
import pytz
import os


class GlobalAuth(HttpBearer):
    def authenticate(self, request, token):
        """
        The function "authenticate" checks if the provided token matches the API key and returns the
        token if they match.

        Args:
            request (obj): The `request` parameter is an object that represents the HTTP request being
                made. It contains information such as the request method, headers, and body.
            token (str): The `token` parameter is a string that represents the authentication token
                provided by the user.

        Returns:
            return: The token is being returned if it matches the API key.
        """

        api_key = config("API_KEY", default=None)
        if token == api_key:
            return token


api = NinjaAPI(auth=GlobalAuth())
api.title = "LenoreFin API"
api.version = "1.0.1"
api.description = "API documentation for LenoreFin"


# The class AccountTypeIn is a schema for validating account types.
class AccountTypeIn(Schema):
    account_type: str
    color: str
    icon: str


# The class AccountTypeOut is a schema for representing account types.
class AccountTypeOut(Schema):
    id: int
    account_type: str
    color: str
    icon: str


# The class BankIn is a schema for validating banks.
class BankIn(Schema):
    bank_name: str


# The class BankOut is a schema for representing banks.
class BankOut(Schema):
    id: int
    bank_name: str


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
    rewards_amount: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)
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
    rewards_amount: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)
    credit_limit: Optional[Decimal] = Field(whole_digits=2, decimal_places=2)
    bank_id: Optional[int]
    last_statement_amount: Optional[Decimal] = Field(
        whole_digits=2, decimal_places=2
    )


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


# The class TagTypeIn is a schema for validating tag types.
class TagTypeIn(Schema):
    tag_type: str


# The class TagTypeOut is a schema for representing tag types.
class TagTypeOut(Schema):
    id: int
    tag_type: str


# The class TagIn is a schema for validating tags.
class TagIn(Schema):
    tag_name: str
    parent_id: Optional[int] = None
    tag_type_id: Optional[int] = None


# The class TagOut is a schema for representing tags.
class TagOut(Schema):
    id: int
    tag_name: str
    parent: Optional["TagOut"] = None
    tag_type: Optional[TagTypeOut] = None


# The class ContribRuleIn is a schema for validating Contribution Rules.
class ContribRuleIn(Schema):
    rule: str
    cap: Optional[str] = None


# The class ContribRuleOut is a schema representing Contribution Rules.
class ContribRuleOut(Schema):
    id: int
    rule: str
    cap: Optional[str] = None


# The class ContributionIn is a schema for validating Contributions.
class ContributionIn(Schema):
    contribution: str
    per_paycheck: Decimal = Field(whole_digits=10, decimal_places=2)
    emergency_diff: Decimal = Field(whole_digits=10, decimal_places=2)
    emergency_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    cap: Decimal = Field(whole_digits=10, decimal_places=2)
    active: bool


# The class ContributionOut is a schema for representing Contributions.
class ContributionOut(Schema):
    id: int
    contribution: str
    per_paycheck: Decimal = Field(whole_digits=10, decimal_places=2)
    emergency_diff: Decimal = Field(whole_digits=10, decimal_places=2)
    emergency_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    cap: Decimal = Field(whole_digits=10, decimal_places=2)
    active: bool


# The class ErrorLevelIn is a schema for validating Error Levels.
class ErrorLevelIn(Schema):
    error_level: str


# The class ErrorLevelOut is a schema for representing Error Levels.
class ErrorLevelOut(Schema):
    id: int
    error_level: str


# The class TransactionTypeIn is a schema for validating transaction types.
class TransactionTypeIn(Schema):
    transaction_type: str


# The class TransactionTypeOut is a schema for representing transaction types.
class TransactionTypeOut(Schema):
    id: int
    transaction_type: str


# The class RepeatIn is a schema for validating Repeat Intervals.
class RepeatIn(Schema):
    repeat_name: str
    days: Optional[int] = 0
    weeks: Optional[int] = 0
    months: Optional[int] = 0
    years: Optional[int] = 0


# The class RepeatOut is a schema for representing Repeat Intervals.
class RepeatOut(Schema):
    id: int
    repeat_name: str
    days: Optional[int] = 0
    weeks: Optional[int] = 0
    months: Optional[int] = 0
    years: Optional[int] = 0


# The class TargetObject is a schema representing a FillObject Target.
class TargetObject(Schema):
    value: int


# The class FillObject is a schema representing a Dataset FillObject.
class FillObject(Schema):
    target: TargetObject
    above: str
    below: str


# The class DatasetObject is a schema representing a Graph Forecast Dataset.
class DatasetObject(Schema):
    borderColor: Optional[str]
    backgroundColor: Optional[str]
    tension: Optional[Decimal] = Field(whole_digits=1, decimal_places=1)
    data: Optional[List[Decimal]] = Field(whole_digits=10, decimal_places=2)
    fill: Optional[FillObject]
    pointStyle: Optional[bool]
    label: Optional[str]
    hoverBackgroundColor: Optional[str] = "rgba(75,192,192,0.6)"
    hoverBorderColor: Optional[str] = "rgba(75,192,192,1)"


# The class GraphData is a schema representing a graph data object.
class GraphData(Schema):
    labels: List[str]
    datasets: List[DatasetObject]


# The class ForecastOut is a schema for representing forecast graph data.
class ForecastOut(Schema):
    labels: List[str]
    datasets: List[DatasetObject]


# The class TagTransactionOut is a schema for representing Transactions by Tag.
class TagTransactionOut(Schema):
    transaction_id: int
    transaction_date: date
    tag_amount: Decimal = Field(whole_digits=10, decimal_places=2)
    transaction_description: str
    transaction_memo: str
    transaction_pretty_account: str


# The class TagGraphOut is a schema for representing a tag bar graph data.
class TagGraphOut(Schema):
    data: GraphData
    year1: int
    year2: int
    year1_avg: Decimal = Field(whole_digits=10, decimal_places=2)
    year2_avg: Decimal = Field(whole_digits=10, decimal_places=2)
    transactions: List[TagTransactionOut]


# The class ReminderIn is a schema for validating Reminders.
class ReminderIn(Schema):
    tag_id: int
    amount: Decimal = Field(whole_digits=10, decimal_places=2)
    reminder_source_account_id: int
    reminder_destination_account_id: Optional[int]
    description: str
    transaction_type_id: int
    start_date: date
    next_date: Optional[date]
    end_date: Optional[date]
    repeat_id: int
    auto_add: bool


# The class ReminderOut is a schema for representing Reminders.
class ReminderOut(Schema):
    id: int
    tag: TagOut
    amount: Decimal = Field(whole_digits=10, decimal_places=2)
    reminder_source_account: AccountOut
    reminder_destination_account: Optional[AccountOut]
    description: str
    transaction_type: TransactionTypeOut
    start_date: date
    next_date: Optional[date]
    end_date: Optional[date]
    repeat: RepeatOut
    auto_add: bool


# The class NoteIn is a schema for validating a Note.
class NoteIn(Schema):
    note_text: str
    note_date: date


# The class NoteOut is a schema for representing a Note.
class NoteOut(Schema):
    id: int
    note_text: str
    note_date: date


# The class OptionIn is a schema for validating Options.
class OptionIn(Schema):
    log_level_id: Optional[int]
    alert_balance: Optional[Decimal] = Field(whole_digits=10, decimal_places=2)
    alert_period: Optional[int]
    widget1_graph_name: Optional[str]
    widget1_tag_id: Optional[int] = None
    widget1_expense: Optional[bool] = True
    widget1_month: Optional[int] = 0
    widget1_exclude: Optional[str] = "[0]"
    widget2_graph_name: Optional[str]
    widget2_tag_id: Optional[int] = None
    widget2_expense: Optional[bool] = True
    widget2_month: Optional[int] = 0
    widget2_exclude: Optional[str] = "[0]"
    widget3_graph_name: Optional[str]
    widget3_tag_id: Optional[int] = None
    widget3_expense: Optional[bool] = True
    widget3_month: Optional[int] = 0
    widget3_exclude: Optional[str] = "[0]"


# The class OptionOut is a schema for representing Options.
class OptionOut(Schema):
    id: int
    log_level: ErrorLevelOut
    alert_balance: Decimal = Field(whole_digits=10, decimal_places=2)
    alert_period: int
    widget1_graph_name: str
    widget1_tag_id: Optional[int] = None
    widget1_expense: bool = True
    widget1_month: int = 0
    widget1_exclude: Optional[str] = "[0]"
    widget2_graph_name: str
    widget2_tag_id: Optional[int] = None
    widget2_expense: bool = True
    widget2_month: int = 0
    widget2_exclude: Optional[str] = "[0]"
    widget3_graph_name: str
    widget3_tag_id: Optional[int] = None
    widget3_expense: bool = True
    widget3_month: int = 0
    widget3_exclude: Optional[str] = "[0]"


# The class TransactionStatusIn is a schema for validating transaction status.
class TransactionStatusIn(Schema):
    transaction_status: str


# The class TransactionStatusOut is a schema for representing transaction status.
class TransactionStatusOut(Schema):
    id: int
    transaction_status: str


# The class PayeeIn is a schema for validating payee information.
class PayeeIn(Schema):
    payee_name: str


# The class PayeeOut is a schema for representing payee information.
class PayeeOut(Schema):
    id: int
    payee_name: str


# The class PayCheckIn is a schema for validating Paycheck information.
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


# The class PayCheckOut is a schema for representing Paycheck information.
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


# The class TagDetailIn is a schema for validating transaction tag details.
class TagDetailIn(Schema):
    tag_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    tag_pretty_name: str
    tag_id: int


# The class TransactionIn is a schema for validating Transaction information.
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
    details: Optional[List[TagDetailIn]] = None
    source_account_id: Optional[int] = None
    destination_account_id: Optional[int] = None
    paycheck: Optional[PaycheckIn] = None
    reminder: Optional[ReminderOut] = None


# The class MessageIn is a schema for validating Messages.
class MessageIn(Schema):
    message_date: datetime
    message: str
    unread: bool


# The class MessageOut is a schema for representing Messages.
class MessageOut(Schema):
    id: int
    message_date: datetime
    message: str
    unread: bool


# The class AllMessage is a schema for representing all messages.
class AllMessage(Schema):
    unread: bool


# The class MessageList is a schema for representing a list of Messages with unread and total count.
class MessageList(Schema):
    unread_count: int
    total_count: int
    messages: List[MessageOut]


def get_today_formatted():
    """
    The function `get_today_formatted` returns the current date in the format "YYYY-MM-DD".

    Returns:
        return: the current date in the format "YYYY-MM-DD".
    """
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz.strftime("%Y-%m-%d")


def get_forecast_start_date(interval):
    """
    The function `get_forecast_start_date` returns the start date for a forecast based on the given
    interval.

    Args:
        interval (int): The interval parameter represents the number of days in the past from today's date.

    Returns:
        return: the start date for a forecast based on the given interval.
    """

    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    startdate = today_tz - timedelta(days=interval)
    return startdate


def get_forecast_end_date(interval):
    """
    The function `get_forecast_end_date` calculates the end date of a forecast based on the given
    interval.

    Args:
        interval (int): The interval parameter represents the number of days from today's date for which
            you want to get the forecast end date.

    Returns:
        return: the end date of the forecast, which is calculated by adding the specified interval (in
            days) to the current date.
    """

    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    enddate = today_tz + timedelta(days=interval)
    return enddate


def get_dates_in_range(start_interval, end_interval):
    """
    The function `get_dates_in_range` returns a list of dates in a specified range, formatted as month,
    day, and year.

    Args:
        start_interval (int): The start_interval parameter represents the starting point of the date range.
            It could be a specific date or a time interval.
        end_interval (int): The `end_interval` parameter represents the end of the date range for which you
            want to generate a list of dates.

    Returns:
        return: a list of dates in the format "Month Day, Year" that fall within the specified start and
            end intervals.
    """

    date_list = []
    current_date = get_forecast_start_date(start_interval)
    end_date = get_forecast_end_date(end_interval)

    while current_date <= end_date:
        date_list.append(current_date.strftime("%b %d, %y"))
        current_date += timedelta(days=1)

    return date_list


def get_unformatted_dates_in_range(start_interval, end_interval):
    """
    The function `get_unformatted_dates_in_range` returns a list of dates within a specified range with no
    formatting.

    Args:
        start_interval (int): The start date of the interval for which you want to get unformatted dates.
        end_interval (int): The `end_interval` parameter represents the end of the date range for which you
            want to get unformatted dates.

    Returns:
        return: a list of unformatted dates within the specified range.
    """

    date_list = []
    current_date = get_forecast_start_date(start_interval)
    end_date = get_forecast_end_date(end_interval)

    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)

    return date_list


# The class TransactionClear is a schema for clearing Transactions.
class TransactionClear(Schema):
    status_id: int
    edit_date: Optional[date] = Field(default_factory=get_today_formatted)


# The class TransactionDetailOut is a schema for representing Transaction Details.
class TransactionDetailOut(Schema):
    id: int
    transaction: "TransactionOut"
    account: AccountOut
    detail_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    tag: TagOut


# The class TransactionOut is a schema for representing Transactions.
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
    balance: Optional[Decimal] = Field(
        default=None, whole_digits=10, decimal_places=2
    )
    pretty_account: Optional[str]
    tags: Optional[List[str]]
    details: List[TransactionDetailOut] = []
    pretty_total: Optional[Decimal] = Field(
        default=None, whole_digits=10, decimal_places=2
    )
    account_id: Optional[int] = None
    source_account_id: Optional[int] = None
    destination_account_id: Optional[int] = None


TransactionDetailOut.update_forward_refs()


# The class PaginatedTransactions is a schema for validating paginated transactions.
class PaginatedTransactions(Schema):
    transactions: List[TransactionOut]
    current_page: int
    total_pages: int
    total_records: int


# The class TransactionDetailIn is a schema for validating Transaction Details.
class TransactionDetailIn(Schema):
    transaction_id: int
    account_id: int
    detail_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    tag_id: int


# The class LogEntryIn is a schema for validating Log Entries.
class LogEntryIn(Schema):
    log_date: Optional[datetime] = None
    log_entry: str
    account_id: Optional[int] = None
    reminder_id: Optional[int] = None
    transaction_id: Optional[int] = None
    error_num: Optional[int] = None
    error_level_id: Optional[int] = None


# The class LogEntryOut is a schema for representing Log Entries.
class LogEntryOut(Schema):
    log_date: datetime
    log_entry: str
    account: Optional[AccountOut] = None
    reminder: Optional[ReminderOut] = None
    transaction: Optional[TransactionOut] = None
    error_num: Optional[int] = None
    error_level: Optional[ErrorLevelOut] = None


# The class GraphDataset is a schema for representing graph datasets.
class GraphDataset(Schema):
    label: str
    data: List[Decimal] = Field(whole_digits=10, decimal_places=2)
    backgroundColor: List[str]
    hoverOffset: int = 4


# The class GraphOut is a schema for representing Graphs.
class GraphOut(Schema):
    labels: List[str]
    datasets: List[GraphDataset]


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


@api.post("/accounts/types")
def create_account_type(request, payload: AccountTypeIn):
    """
    The function `create_account_type` creates an account type

    Args:
        request ():
        payload (AccountTypeIn): An object using schema of AccountTypeIn.

    Returns:
        id: returns the id of the created account type
    """

    try:
        account_type = AccountType.objects.create(**payload.dict())
        logToDB(
            f"Account type created : {account_type.account_type}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": account_type.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Account type not created : type exists ({payload.account_type})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Account type already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Account type not created : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account type not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@api.post("/accounts/banks")
def create_bank(request, payload: BankIn):
    """
    The function `create_bank` creates a bank

    Args:
        request ():
        payload (BankIn): An object using schema of BankIn.

    Returns:
        id: returns the id of the created bank
    """

    try:
        bank = Bank.objects.create(**payload.dict())
        logToDB(
            f"Bank created : {bank.bank_name}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": bank.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Bank not created : bank exists ({payload.bank_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Bank already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Bank not created : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Bank not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@api.post("/accounts")
def create_account(request, payload: AccountIn):
    """
    The function `create_account` creates an account

    Args:
        request ():
        payload (AccountIn): An object using schema of AccountIn.

    Returns:
        id: returns the id of the created account
    """

    try:
        account = Account.objects.create(**payload.dict())
        logToDB(
            f"Account created : {account.account_name}",
            account.id,
            None,
            None,
            3001001,
            1,
        )
        return {"id": account.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Account not created : name exists ({payload.account_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Account name already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Account not created : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@api.post("/tags")
def create_tag(request, payload: TagIn):
    """
    The function `create_tag` creates a tag

    Args:
        request ():
        payload (TagIn): An object using schema of TagIn.

    Returns:
        id: returns the id of the created tag
    """

    try:
        tag = Tag.objects.create(**payload.dict())
        logToDB(
            f"Tag created : {tag.tag_name}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": tag.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Tag not created : tag exists ({payload.tag_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Tag already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Tag not created : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Tag not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@api.post("/planning/contribrules")
def create_contrib_rule(request, payload: ContribRuleIn):
    """
    The function `create_contrib_rule` creates a contribution rule

    Args:
        request ():
        payload (ContribRuleIn): An object using schema of ContribRuleIn.

    Returns:
        id: returns the id of the created contribution rule
    """

    try:
        contrib_rule = ContribRule.objects.create(**payload.dict())
        logToDB(
            f"Contribution rule created : {payload.rule}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": contrib_rule.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Contribution rule not created : rule exists ({payload.rule})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Conitribution rule already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Contribution rule not created : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution rule not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@api.post("/planning/contributions")
def create_contribution(request, payload: ContributionIn):
    """
    The function `create_contribution` creates a contribution

    Args:
        request ():
        payload (ContributionIn): An object using schema of ContributionIn.

    Returns:
        id: returns the id of the created contribution
    """

    try:
        contribution = Contribution.objects.create(**payload.dict())
        logToDB(
            f"Contribution created : {payload.contribution}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": contribution.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Contribution not created : contribution exists ({payload.contribution})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Conitribution already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Contribution not created : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@api.post("/reminders/repeats")
def create_repeat(request, payload: RepeatIn):
    """
    The function `create_repeat` creates a repeat

    Args:
        request ():
        payload (RepeatIn): An object using schema of RepeatIn.

    Returns:
        id: returns the id of the created repeat
    """

    try:
        repeat = Repeat.objects.create(**payload.dict())
        logToDB(
            f"Repeat created : {repeat.repeat_name}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": repeat.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Repeat not created : repeat exists ({payload.repeat_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Repeat already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Repeat not created : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Repeat not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@api.post("/reminders")
def create_reminder(request, payload: ReminderIn):
    """
    The function `create_reminder` creates a reminder

    Args:
        request ():
        payload (ReminderIn): An object using schema of ReminderIn.

    Returns:
        id: returns the id of the created reminder
    """

    try:
        reminder = Reminder.objects.create(**payload.dict())
        logToDB(
            f"Reminder created : {reminder.description}",
            None,
            reminder.id,
            None,
            3001001,
            1,
        )
        reminder_trans_add(reminder.id)
        return {"id": reminder.id}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Reminder not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@api.post("/planning/notes")
def create_note(request, payload: NoteIn):
    """
    The function `create_note` creates a note

    Args:
        request ():
        payload (NoteIn): An object using schema of NoteIn.

    Returns:
        id: returns the id of the created note
    """

    try:
        note = Note.objects.create(**payload.dict())
        logToDB(
            f"Note created : {note.note_date}",
            None,
            None,
            None,
            3001005,
            2,
        )
        return {"id": note.id}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Note not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@api.post("/payees")
def create_payee(request, payload: PayeeIn):
    """
    The function `create_payee` creates a payee

    Args:
        request ():
        payload (PayeeIn): An object using schema of PayeeIn.

    Returns:
        id: returns the id of the created payee
    """

    try:
        payee = Payee.objects.create(**payload.dict())
        logToDB(
            f"Payee created : {payee.payee_name}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": payee.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Payee not created : payee exists ({payload.payee_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Payee already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Payee not created : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Payee not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@api.post("/paychecks")
def create_paycheck(request, payload: PaycheckIn):
    """
    The function `create_paycheck` creates a paycheck

    Args:
        request ():
        payload (PaycheckIn): An object using schema of PaycheckIn.

    Returns:
        id: returns the id of the created paycheck
    """

    try:
        paycheck = Paycheck.objects.create(**payload.dict())
        logToDB(
            f"Paycheck created : #{paycheck.id}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": paycheck.id}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Paycheck not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@api.post("/transactions")
def create_transaction(request, payload: TransactionIn):
    """
    The function `create_transaction` creates a transaction

    Args:
        request ():
        payload (TransactionIn): An object using schema of TransactionIn.

    Returns:
        id: returns the id of the created transaction
    """

    try:
        transaction = None
        paycheck_id = None
        transactions_to_create = []
        tags = []
        # Create paycheck
        if payload.paycheck is not None:
            paycheck = Paycheck.objects.create(
                gross=payload.paycheck.gross,
                net=payload.paycheck.net,
                taxes=payload.paycheck.taxes,
                health=payload.paycheck.health,
                pension=payload.paycheck.pension,
                fsa=payload.paycheck.fsa,
                dca=payload.paycheck.dca,
                union_dues=payload.paycheck.union_dues,
                four_fifty_seven_b=payload.paycheck.four_fifty_seven_b,
                payee_id=payload.paycheck.payee_id,
            )
            paycheck_id = paycheck.id
        if payload.details is not None:
            for detail in payload.details:
                tag_obj = CustomTag(
                    tag_name=detail.tag_pretty_name,
                    tag_amount=detail.tag_amt,
                    tag_id=detail.tag_id,
                )
                tags.append(tag_obj)
        transaction = FullTransaction(
            transaction_date=payload.transaction_date,
            total_amount=payload.total_amount,
            status_id=payload.status_id,
            memo=payload.memo,
            description=payload.description,
            edit_date=payload.edit_date,
            add_date=payload.add_date,
            transaction_type_id=payload.transaction_type_id,
            reminder_id=payload.reminder_id,
            paycheck_id=paycheck_id,
            source_account_id=payload.source_account_id,
            destination_account_id=payload.destination_account_id,
            tags=tags,
        )
        transactions_to_create.append(transaction)
        if create_transactions(transactions_to_create):
            logToDB(
                "Transaction created",
                None,
                None,
                None,
                3001005,
                1,
            )

            return {"id": None}
        else:
            raise Exception("Error creating transaction")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, f"Record creation error : {str(e)}")


@api.post("/transactions/details")
def create_transaction_detail(request, payload: TransactionDetailIn):
    """
    The function `create_transaction_detail` creates a transaction detail

    Args:
        request ():
        payload (TransactionDetailIn): An object using schema of TransactionDetailIn.

    Returns:
        id: returns the id of the created transaction detail
    """

    try:
        transaction_detail = TransactionDetail.objects.create(**payload.dict())
        logToDB(
            f"Transaction detail created : #{transaction_detail.transaction.id}",
            None,
            None,
            payload.transaction_id,
            3001005,
            2,
        )
        return {"id": transaction_detail.id}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction detail not created : {str(e)}",
            None,
            None,
            payload.transaction_id,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@api.post("/logentries")
def create_log_entry(request, payload: LogEntryIn):
    """
    The function `create_log_entry` creates a log entry, but only if the log_level_id
    is greater than the current log_level in options

    Args:
        request ():
        payload (LogEntryIn): An object using schema of LogEntryIn.

    Returns:
        id: returns and id of 0
    """

    options = get_object_or_404(Option, id=1)
    if payload.error_level_id >= options.log_level.id:
        log_entry = LogEntry.objects.create(**payload.dict())
        return {"id": log_entry.id}
    return {"id": 0}


@api.post("/messages")
def create_message(request, payload: MessageIn):
    """
    The function `create_transaction_detail` creates a transaction detail

    Args:
        request ():
        payload (TransactionDetailIn): An object using schema of TransactionDetailIn.

    Returns:
        id: returns the id of the created transaction detail
    """

    try:
        message = Message.objects.create(**payload.dict())
        logToDB(
            f"Message created : #{message.id}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": message.id}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Message not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@api.get("/accounts/types/{accounttype_id}", response=AccountTypeOut)
def get_account_type(request, accounttype_id: int):
    """
    The function `get_account_type` retrieves the account type by id

    Args:
        request (HttpRequest): The HTTP request object
        accounttype_id (int): The id of the account type to retrieve.

    Returns:
        AccountTypeOut: the account type object

    Raises:
        Http404: If the account type with the specified ID does not exist.
    """

    try:
        account_type = get_object_or_404(AccountType, id=accounttype_id)
        logToDB(
            f"Account type retrieved : {account_type.account_type}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return account_type
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account type not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/accounts/banks/{bank_id}", response=BankOut)
def get_bank(request, bank_id: int):
    """
    The function `get_bank` retrieves the bank by id

    Args:
        request (HttpRequest): The HTTP request object
        bank_id (int): The id of the bank to retrieve.

    Returns:
        BankOut: the bank object

    Raises:
        Http404: If the bank with the specified ID does not exist.
    """

    try:
        bank = get_object_or_404(Bank, id=bank_id)
        logToDB(
            f"Bank retrieved : {bank.bank_name}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return bank
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Bank not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/accounts/{account_id}", response=AccountOut)
def get_account(request, account_id: int):
    """
    The function `get_account` retrieves the account by id

    Args:
        request (HttpRequest): The HTTP request object.
        account_id (int): The id of the account to retrieve.

    Returns:
        AccountOut: the account object

    Raises:
        Http404: If the account with the specified ID does not exist.
    """

    try:
        # Retrieve the account object from the database
        account = get_object_or_404(Account, id=account_id)

        # Fetch last transaction running_total, excluding pending
        calc_balance = account.opening_balance
        if Transaction.objects.filter(account_id=account_id).exclude(
            status_id=1
        ):
            calc_balance = (
                sort_transactions(
                    Transaction.objects.filter(account_id=account_id).exclude(
                        status_id=1
                    ),
                    False,
                )
                .first()
                .running_total
            )

        # Prepare the AccountOut object
        account_out = AccountOut(
            id=account.id,
            account_name=account.account_name,
            account_type=AccountTypeOut(
                id=account.account_type.id,
                account_type=account.account_type.account_type,
                color=account.account_type.color,
                icon=account.account_type.icon,
            ),
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
            last_statement_amount=account.last_statement_amount,
        )
        logToDB(
            f"Account retrieved : {account_out.account_name}",
            account_id,
            None,
            None,
            3001006,
            1,
        )
        return account_out
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account not retrieved : {str(e)}",
            account_id,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/tags/{tag_id}", response=TagOut)
def get_tag(request, tag_id: int):
    """
    The function `get_tag` retrieves the tag by id

    Args:
        request (HttpRequest): The HTTP request object.
        tag_id (int): The id of the tag to retrieve.

    Returns:
        TagOut: the tag object

    Raises:
        Http404: If the tag with the specified ID does not exist.
    """

    try:
        tag = get_object_or_404(Tag, id=tag_id)
        logToDB(
            f"Tag retrieved : {tag.tag_name}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return tag
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Tag not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/planning/contribrules/{contribrule_id}", response=ContribRuleOut)
def get_contribrule(request, contribrule_id: int):
    """
    The function `get_contribrule` retrieves the contribution rule by id

    Args:
        request (HttpRequest): The HTTP request object.
        contribrule_id (int): The id of the contribution rule to retrieve.

    Returns:
        ContribRuleOut: the contribution rule object

    Raises:
        Http404: If the contribution rule with the specified ID does not exist.
    """

    try:
        contrib_rule = get_object_or_404(ContribRule, id=contribrule_id)
        logToDB(
            f"Contribution rule retrieved : {contrib_rule.rule}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return contrib_rule
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution rule not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/planning/contributions/{contribution_id}", response=ContributionOut)
def get_contribution(request, contribution_id: int):
    """
    The function `get_contribution` retrieves the contribution by id

    Args:
        request (HttpRequest): The HTTP request object.
        contribution_id (int): The id of the contribution to retrieve.

    Returns:
        ContributionOut: the contribution object

    Raises:
        Http404: If the contribution with the specified ID does not exist.
    """

    try:
        contribution = get_object_or_404(Contribution, id=contribution_id)
        logToDB(
            f"Contribution retrieved : {contribution.rule}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return contribution
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/errorlevels/{errorlevel_id}", response=ErrorLevelOut)
def get_errorlevel(request, errorlevel_id: int):
    """
    The function `get_errorlevel` retrieves the error level by id

    Args:
        request (HttpRequest): The HTTP request object.
        errorlevel_id (int): The id of the error level to retrieve.

    Returns:
        ErrorLevelOut: the error level object

    Raises:
        Http404: If the error level with the specified ID does not exist.
    """

    try:
        errorlevel = get_object_or_404(ErrorLevel, id=errorlevel_id)
        logToDB(
            f"Error level retrieved : {errorlevel.error_level}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return errorlevel
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Error level not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get(
    "/transaction/types/{transaction_type_id}", response=TransactionTypeOut
)
def get_transaction_type(request, transaction_type_id: int):
    """
    The function `get_transaction_type` retrieves the transaction type by id

    Args:
        request (HttpRequest): The HTTP request object.
        transaction_type_id (int): The id of the transaction type to retrieve.

    Returns:
        TransactionTypeOut: the transaction type object

    Raises:
        Http404: If the transaction type with the specified ID does not exist.
    """

    try:
        transaction_type = get_object_or_404(
            TransactionType, id=transaction_type_id
        )
        logToDB(
            f"Transaction type retrieved : {transaction_type.transaction_type}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return transaction_type
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction type not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/reminders/repeats/{repeat_id}", response=RepeatOut)
def get_repeat(request, repeat_id: int):
    """
    The function `get_repeat` retrieves the repeat by id

    Args:
        request (HttpRequest): The HTTP request object.
        repeat_id (int): The id of the repeat to retrieve.

    Returns:
        RepeatOut: the repeat object

    Raises:
        Http404: If the repeat with the specified ID does not exist.
    """

    try:
        repeat = get_object_or_404(Repeat, id=repeat_id)
        logToDB(
            f"Repeat retrieved : {repeat.repeat_name}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return repeat
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Repeat not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/reminders/{reminder_id}", response=ReminderOut)
def get_reminder(request, reminder_id: int):
    """
    The function `get_reminder` retrieves the reminder by id

    Args:
        request (HttpRequest): The HTTP request object.
        reminder_id (int): The id of the reminder to retrieve.

    Returns:
        ReminderOut: the reminder object

    Raises:
        Http404: If the reminder with the specified ID does not exist.
    """

    try:
        reminder = get_object_or_404(Reminder, id=reminder_id)
        logToDB(
            f"Reminder retrieved : {reminder.description}",
            None,
            reminder.id,
            None,
            3001006,
            1,
        )
        return reminder
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Reminder not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/planning/notes/{note_id}", response=NoteOut)
def get_note(request, note_id: int):
    """
    The function `get_note` retrieves the note by id

    Args:
        request (HttpRequest): The HTTP request object.
        note_id (int): The id of the note to retrieve.

    Returns:
        NoteOut: the note object

    Raises:
        Http404: If the note with the specified ID does not exist.
    """

    try:
        note = get_object_or_404(Note, id=note_id)
        logToDB(
            f"Note retrieved : #{note.id}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return note
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Note not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/options/{option_id}", response=OptionOut)
def get_option(request, option_id: int):
    """
    The function `get_option` retrieves the option by id

    Args:
        request (HttpRequest): The HTTP request object.
        option_id (int): The id of the option to retrieve.

    Returns:
        OptionOut: the option object

    Raises:
        Http404: If the option with the specified ID does not exist.
    """

    try:
        option = get_object_or_404(Option, id=option_id)
        logToDB(
            f"Option retrieved : #{option.id}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return option
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Option not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/accounts/{account_id}/forecast", response=ForecastOut)
def get_forecast(
    request, account_id: int, start_interval: int, end_interval: int
):
    """
    The function `get_forecast` retrieves the forecast data for the account id

    Args:
        request (HttpRequest): The HTTP request object.
        account_id (int): The id of the account to retrieve forecast data.
        start_interval (int): the number of days before today to start forecast.
        end_interval (int): the number of days after today to end forecast.

    Returns:
        ForecastOut: the forecast object

    Raises:
        Http404: If the account with the specified ID does not exist.
    """

    try:
        # Retrieve the dates in range as labels for forecast
        labels = get_dates_in_range(start_interval, end_interval)

        dates = get_unformatted_dates_in_range(start_interval, end_interval)
        data = []
        datasets = []
        opening_balance = Account.objects.get(id=account_id).opening_balance

        # Retrieve the transactions in the date range for the account
        start_date = get_forecast_start_date(start_interval)
        end_date = get_forecast_end_date(end_interval)
        lowest_source_balance_object = sort_transactions(
            Transaction.objects.filter(
                account_id=account_id, transaction_date__lt=start_date
            )
        ).last()
        transactions = sort_transactions(
            Transaction.objects.filter(
                Q(account_id=account_id),
                transaction_date__range=(start_date, end_date),
            )
        )

        # Calculate the daily account balance
        balance = Decimal(0)
        if lowest_source_balance_object is None:
            balance = opening_balance
        else:
            balance = lowest_source_balance_object.running_total
        day_balance = Decimal(0)
        for label in dates:
            last_transaction_of_day = sort_transactions(
                transactions.filter(transaction_date=label)
            ).last()
            if last_transaction_of_day:
                day_balance = last_transaction_of_day.running_total
                balance = day_balance
            else:
                day_balance = balance
            data.append(day_balance)

        # Prepare the graph data for the forecast object
        targetobject_out = TargetObject(value=0)
        fillobject_out = FillObject(
            target=targetobject_out,
            above="rgb(236 , 253, 245)",
            below="rgb(248, 121, 121)",
        )
        datasets_out = DatasetObject(
            borderColor="#06966A",
            backgroundColor="#06966A",
            tension=0.1,
            data=data,
            fill=fillobject_out,
            pointStyle="false",
        )
        datasets.append(datasets_out)
        forecast_out = ForecastOut(labels=labels, datasets=datasets)
        logToDB(
            "Forecast retrieved",
            account_id,
            None,
            None,
            3002002,
            1,
        )
        return forecast_out
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Forecast not retrieved : {str(e)}",
            account_id,
            None,
            None,
            3002902,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get(
    "/transaction/statuses/{transactionstatus_id}",
    response=TransactionStatusOut,
)
def get_transaction_status(request, transactionstatus_id: int):
    """
    The function `get_transaction_status` retrieves the transaction status by id

    Args:
        request (HttpRequest): The HTTP request object.
        transactionstatus_id (int): The id of the transaction status to retrieve.

    Returns:
        TransactionStatusOut: the transaction status object

    Raises:
        Http404: If the transaction status with the specified ID does not exist.
    """

    try:
        transaction_status = get_object_or_404(
            TransactionStatus, id=transactionstatus_id
        )
        logToDB(
            f"Transaction status retrieved : {transaction_status.transaction_status}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return transaction_status
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction status not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/payees/{payee_id}", response=PayeeOut)
def get_payee(request, payee_id: int):
    """
    The function `get_payee` retrieves the payee by id

    Args:
        request (HttpRequest): The HTTP request object.
        payee_id (int): The id of the payee to retrieve.

    Returns:
        PayeeOut: the payee object

    Raises:
        Http404: If the payee with the specified ID does not exist.
    """

    try:
        payee = get_object_or_404(Payee, id=payee_id)
        logToDB(
            f"Payee retrieved : {payee.payee_name}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return payee
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Payee not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/paychecks/{paycheck_id}", response=PaycheckOut)
def get_paycheck(request, paycheck_id: int):
    """
    The function `get_paycheck` retrieves the paycheck by id

    Args:
        request (HttpRequest): The HTTP request object.
        paycheck_id (int): The id of the paycheck to retrieve.

    Returns:
        PaycheckOut: the payee object

    Raises:
        Http404: If the paycheck with the specified ID does not exist.
    """

    try:
        paycheck = get_object_or_404(Paycheck, id=paycheck_id)
        logToDB(
            f"Paycheck retrieved : #{paycheck.id}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return paycheck
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Paycheck not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/transactions/{transaction_id}", response=TransactionOut)
def get_transaction(request, transaction_id: int):
    """
    The function `get_transaction` retrieves the transaction by id

    Args:
        request (HttpRequest): The HTTP request object.
        transaction_id (int): The id of the transaction to retrieve.

    Returns:
        TransactionOut: the transaction object

    Raises:
        Http404: If the transaction with the specified ID does not exist.
    """

    try:
        transaction = get_object_or_404(Transaction, id=transaction_id)
        logToDB(
            f"Transaction retrieved : #{transaction.id}",
            None,
            None,
            transaction.id,
            3001006,
            1,
        )
        return transaction
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get(
    "/transactions/details/{transactiondetail_id}",
    response=TransactionDetailOut,
)
def get_transaction_detail(request, transactiondetail_id: int):
    """
    The function `get_transaction_detail` retrieves the transaction detail by id

    Args:
        request (HttpRequest): The HTTP request object.
        transactiondetail_id (int): The id of the transaction detail to retrieve.

    Returns:
        TransactionDetailOut: the transaction detail object

    Raises:
        Http404: If the transaction detail with the specified ID does not exist.
    """

    try:
        transaction_detail = get_object_or_404(
            TransactionDetail, id=transactiondetail_id
        )
        logToDB(
            f"Transaction detail retrieved : #{transaction_detail.id}",
            None,
            None,
            transaction_detail.transaction.id,
            3001006,
            1,
        )
        return transaction_detail
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction detail not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/logentries/{logentry_id}", response=LogEntryOut)
def get_log_entry(request, logentry_id: int):
    """
    The function `get_log_entry` retrieves the log entry by id

    Args:
        request (HttpRequest): The HTTP request object.
        logentry_id (int): The id of the log entry to retrieve.

    Returns:
        LogEntryOut: the log entry object

    Raises:
        Http404: If the log entry with the specified ID does not exist.
    """

    try:
        log_entry = get_object_or_404(LogEntry, id=logentry_id)
        logToDB(
            f"Log entry retrieved : #{log_entry.id}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return log_entry
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Log entry not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/messages/{message_id}", response=MessageOut)
def get_message(request, message_id: int):
    """
    The function `get_message` retrieves the message by id

    Args:
        request (HttpRequest): The HTTP request object.
        message_id (int): The id of the message to retrieve.

    Returns:
        MessageOut: the message object

    Raises:
        Http404: If the message with the specified ID does not exist.
    """

    try:
        message = get_object_or_404(Message, id=message_id)
        logToDB(
            f"Message retrieved : {message.id}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return message
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Message not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/accounts/types", response=List[AccountTypeOut])
def list_account_types(request):
    """
    The function `list_account_types` retrieves a list of account types,
    orderd by ID ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        AccountTypeOut: a list of account type objects
    """

    try:
        qs = AccountType.objects.all().order_by("id")
        logToDB(
            "Account type list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account type list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/accounts/banks", response=List[BankOut])
def list_banks(request):
    """
    The function `list_banks` retrieves a list of banks,
    orderd by bank name ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        BankOut: a list of bank objects
    """

    try:
        qs = Bank.objects.all().order_by("bank_name")
        logToDB(
            "Bank list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Bank list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/graphs_bytags", response=GraphOut)
def get_graph(request, widget_id: int):
    """
    The function `get_graph` retrieves graph data for tags for widget id.

    Args:
        request (HttpRequest): The HTTP request object.
        widget_id (int): The widget for graph data

    Returns:
        GraphOut: the graph data object
    """

    try:
        # Initialize variables
        graph_name = ""
        exclude = "[0]"
        tagID = None
        month = 0
        expense = True

        # Load the options for the specified widget ID
        options = get_object_or_404(Option, id=1)

        # Set graph options based on widget options
        if widget_id == 1:
            graph_name = options.widget1_graph_name
            exclude = options.widget1_exclude
            tagID = options.widget1_tag_id
            month = options.widget1_month
            expense = options.widget1_expense
        if widget_id == 2:
            graph_name = options.widget2_graph_name
            exclude = options.widget2_exclude
            tagID = options.widget2_tag_id
            month = options.widget2_month
            expense = options.widget2_expense
        if widget_id == 3:
            graph_name = options.widget3_graph_name
            exclude = options.widget3_exclude
            tagID = options.widget3_tag_id
            month = options.widget3_month
            expense = options.widget3_expense
        exclude_list = json.loads(exclude)
        today = timezone.now()
        tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
        today_tz = today.astimezone(tz_timezone).date()
        target_date = today_tz - relativedelta(months=month)
        target_month = target_date.month
        target_year = target_date.year
        labels = []
        values = []
        datasets = []
        colors = [
            "#7fb1b1",
            "#597c7c",
            "#7f8cb1",
            "#7fb17f",
            "#597c59",
            "#b17fa5",
            "#7c5973",
            "#b1a77f",
            "#edffff",
            "#dbffff",
            "#7c6759",
            "#b1937f",
            "#8686b1",
            "#5e5e7c",
            "#757c59",
            "#52573e",
            "#ffedff",
            "#573e57",
            "#fff8db",
            "#ffe9db",
            "#e0e0ff",
            "#9d9db3",
        ]

        # Sort colors randomly, seeded to stay the same for this month
        random.seed(today_tz.month * widget_id)
        random.shuffle(colors)

        # If a tag is specified in options, filter by that tag
        # Otherwise, filter on expense tags or income tags
        if tagID is None:
            tag_type_id = 1 if expense else 2
            tags = Tag.objects.filter(
                tag_type__id=tag_type_id, parent=None
            ).exclude(id__in=exclude_list)
        else:
            tags = Tag.objects.filter(parent__id=tagID).exclude(
                id__in=exclude_list
            )

        # Calculate month totals for each tag
        # Use the tag name as the label and the total as the value
        for tag in tags:
            tag_amount = (
                TransactionDetail.objects.filter(
                    Q(tag=tag) | Q(tag__parent=tag),
                    transaction__transaction_date__month=target_month,
                    transaction__transaction_date__year=target_year,
                    transaction__status__id__gt=1,
                ).aggregate(Sum("detail_amt"))["detail_amt__sum"]
                or 0
            )
            if tag_amount != 0:
                labels.append(tag.tag_name)
                values.append(tag_amount)

        # If there are no tags or totals, return None as label and 0 as value
        if not values:
            values.append(0)
        if not labels:
            labels.append("None")

        # Prepare the graph data object
        dataset = GraphDataset(
            label=graph_name, data=values, backgroundColor=colors, hoverOffset=4
        )
        datasets.append(dataset)
        graph_object = GraphOut(labels=labels, datasets=datasets)
        logToDB(
            f"Graph data retrieved : {widget_id}",
            None,
            None,
            None,
            3002003,
            1,
        )
        return graph_object
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Graph data not retrieved : {str(e)}",
            None,
            None,
            None,
            3002903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/transactions_bytag", response=TagGraphOut)
def list_transactions_bytag(request, tag: int):
    """
    The function `list_transactions_bytag` retrieves transactions for a tag id,
    and calcualtes the totals by month for the current year and last year, as
    well as the averages by month for the years and returns the data as graph
    data.

    Args:
        request (HttpRequest): The HTTP request object.
        tag (int): The tag id to get transactions for.
        month (int): Optional month integer.  If none is provided, 0

    Returns:
        TagDetailOut: the tag detail object
    """

    try:
        # Calculate dates based on month, year
        today = timezone.now()
        tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
        today_tz = today.astimezone(tz_timezone).date()
        this_month = today_tz.month
        this_year = today_tz.year
        last_year = today_tz.year - 1

        # Retrieve all transactions for tag
        alltrans = TransactionDetail.objects.filter(
            Q(tag__id=tag) & Q(transaction__status__id__gt=1)
        ).order_by("-transaction__transaction_date")

        # Filter transactions for current year
        thisyear_trans = alltrans.filter(
            transaction__transaction_date__year=this_year
        ).order_by("-transaction__transaction_date")

        # Filter transactions for last year
        lastyear_trans = alltrans.filter(
            transaction__transaction_date__year=last_year
        ).order_by("-transaction__transaction_date")

        # Calculate the YTD total
        this_year_total = 0
        this_year_total = thisyear_trans.aggregate(
            total_amount=Sum("detail_amt")
        )["total_amount"]
        if this_year_total is not None:
            this_year_total = abs(this_year_total)
        else:
            this_year_total = 0

        # Calculate last years total
        last_year_total = 0
        last_year_total = lastyear_trans.aggregate(
            total_amount=Sum("detail_amt")
        )["total_amount"]
        if last_year_total is not None:
            last_year_total = abs(last_year_total)
        else:
            last_year_total = 0

        # Calculate YTD Monthly average
        if this_year_total is not None:
            this_year_avg = this_year_total / this_month
        else:
            this_year_avg = 0
        this_year_avg = round(this_year_avg, 2)
        # Calculate Last Year Monthly average
        if last_year_total is not None:
            last_year_avg = last_year_total / 12
        else:
            last_year_avg = 0
        last_year_avg = round(last_year_avg, 2)
        # Prepare the transactions object
        transaction_details = []
        for detail in alltrans:
            transaction_detail = TagTransactionOut(
                transaction_id=detail.transaction.id,
                transaction_date=detail.transaction.transaction_date,
                tag_amount=detail.detail_amt,
                transaction_description=detail.transaction.description,
                transaction_memo=detail.transaction.memo,
                transaction_pretty_account=detail.account.account_name,
            )
            transaction_details.append(transaction_detail)

        # Calculate this year monthly totals
        this_year_totals = []
        for month in range(1, this_month + 1):
            monthly_total = 0
            monthly_total = thisyear_trans.filter(
                transaction__transaction_date__month=month
            ).aggregate(monthly_total=Sum("detail_amt"))["monthly_total"]
            if monthly_total is not None:
                this_year_totals.append(abs(monthly_total))
            else:
                this_year_totals.append(0)

        # Calculate last year monthly totals
        last_year_totals = []
        for month in range(1, 13):
            monthly_total = 0
            monthly_total = lastyear_trans.filter(
                transaction__transaction_date__month=month
            ).aggregate(monthly_total=Sum("detail_amt"))["monthly_total"]
            if monthly_total is not None:
                last_year_totals.append(abs(monthly_total))
            else:
                last_year_totals.append(0)

        # Prepare the datasets
        datasets = []
        this_year_dataset = DatasetObject(
            label=this_year, backgroundColor="#046959", data=this_year_totals
        )
        datasets.append(this_year_dataset)
        last_year_dataset = DatasetObject(
            label=last_year, backgroundColor="#c2fff5", data=last_year_totals
        )
        datasets.append(last_year_dataset)

        # Prepare the GraphData object
        graph_data = GraphData(
            labels=[
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ],
            datasets=datasets,
        )

        # Prepare the tag graph out object
        tag_graph_out = TagGraphOut(
            data=graph_data,
            year1=this_year,
            year2=last_year,
            year1_avg=this_year_avg,
            year2_avg=last_year_avg,
            transactions=transaction_details,
        )
        logToDB(
            f"Tag details retrieved : {tag}",
            None,
            None,
            None,
            3002004,
            1,
        )
        return tag_graph_out
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Tag details not retrieved : {str(e)}",
            None,
            None,
            None,
            3002904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/accounts", response=List[AccountOut])
def list_accounts(
    request,
    account_type: Optional[int] = Query(None),
    inactive: Optional[bool] = Query(None),
):
    """
    The function `list_accounts` retrieves a list of accounts,
    optionally filtered by inactive or account type.

    Args:
        request (HttpRequest): The HTTP request object.
        account_type (int): Optional account type id to filter accounts.
        inactive (bool): Optional filter on inactive or not

    Returns:
        AccountOut: a list of Account objects
    """

    try:
        # Retrieve all accounts
        qs = Account.objects.all()

        # If inactive argument is provided, filter by active/inactive
        if not inactive:
            qs = qs.filter(active=True)

        # If account type argument is provided, filter by account type
        if account_type is not None and account_type != 0:
            qs = qs.filter(account_type__id=account_type)

        if account_type is not None and account_type == 0:
            qs = qs.filter(active=False)

        # Order accounts by account type id ascending, bank name ascending, and account
        # name ascending
        qs = qs.order_by("account_type__id", "bank__bank_name", "account_name")

        # Initialize blank account list
        account_list = []

        # For each account, get related transactions and calculate balance
        for account in qs:
            calc_balance = account.opening_balance
            if Transaction.objects.filter(account_id=account.id).exclude(
                status_id=1
            ):
                calc_balance = (
                    sort_transactions(
                        Transaction.objects.filter(
                            account_id=account.id
                        ).exclude(status_id=1),
                        False,
                    )
                    .first()
                    .running_total
                )

            # Prepare Account object
            account_out = AccountOut(
                id=account.id,
                account_name=account.account_name,
                account_type=AccountTypeOut(
                    id=account.account_type.id,
                    account_type=account.account_type.account_type,
                    color=account.account_type.color,
                    icon=account.account_type.icon,
                ),
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
                bank=BankOut(
                    id=account.bank.id, bank_name=account.bank.bank_name
                ),
                last_statement_amount=account.last_statement_amount,
            )
            account_list.append(account_out)
        logToDB(
            "Account list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return account_list
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/tags", response=List[TagOut])
def list_tags(
    request,
    tag_type: Optional[int] = Query(None),
    parent_only: Optional[bool] = False,
):
    """
    The function `list_tags` retrieves a list of tags,
    optionally filtered by tag type or if its a parent tag.

    Args:
        request (HttpRequest): The HTTP request object.
        tag_type (int): Optional tag type id to filter tags.
        parent_only (bool): Optional filter on parent or not

    Returns:
        TagOut: a list of tag objects
    """

    try:
        # Retrive a list of tags, annotating a pretty_name based on parent tag name
        qs = Tag.objects.annotate(
            pretty_name=Case(
                When(
                    parent__isnull=False,
                    then=Concat(
                        F("parent__tag_name"), Value(" / "), F("tag_name")
                    ),
                ),
                default=F("tag_name"),
                output_field=CharField(),
            )
        )

        # Filter tags by tag type if a tag type is specified
        if tag_type is not None:
            qs = qs.filter(tag_type__id=tag_type)

        # Filter tags by parent if parent only is true
        if parent_only is True:
            qs = qs.filter(parent__isnull=True).exclude(tag_type__id=3)

        # Order tags by pretty name ascending, parent tag name ascending, and then tag name
        # ascending
        qs = qs.order_by("pretty_name", "parent__tag_name", "tag_name")
        logToDB(
            "Tag list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Tag list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/planning/contribrules", response=List[ContribRuleOut])
def list_contrib_rules(request):
    """
    The function `list_contrib_rules` retrieves a list of contribution rules,
    orderd by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        ContribRuleOut: a list of contribution rule objects
    """

    try:
        qs = ContribRule.objects.all().order_by("id")
        logToDB(
            "Contribution rule list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution rule list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/planning/contributions", response=List[ContributionOut])
def list_contributions(request):
    """
    The function `list_contributions` retrieves a list of contributions,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        ContributionOut: a list of contribution objects
    """

    try:
        qs = Contribution.objects.all().order_by("id")
        logToDB(
            "Contribution list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/errorlevels", response=List[ErrorLevelOut])
def list_errorlevels(request):
    """
    The function `list_errorlevels` retrieves a list of error levels,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        ErrorLevelOut: a list of error level objects
    """

    try:
        qs = ErrorLevel.objects.all().order_by("id")
        logToDB(
            "Error level list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Error level list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/transaction/types", response=List[TransactionTypeOut])
def list_transaction_types(request):
    """
    The function `list_transaction_types` retrieves a list of transaction types,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        TransactionTypeOut: a list of transaction type objects
    """

    try:
        qs = TransactionType.objects.all().order_by("id")
        logToDB(
            "Transaction type list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction type list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/reminders/repeats", response=List[RepeatOut])
def list_repeats(request):
    """
    The function `list_repeats` retrieves a list of repeats,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        RepeatOut: a list of repeat objects
    """

    try:
        qs = Repeat.objects.all().order_by("id")
        logToDB(
            "Repeat list not retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Repeat list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/reminders", response=List[ReminderOut])
def list_reminders(request):
    """
    The function `list_reminders` retrieves a list of reminders,
    ordered by next date ascending and then id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        ReminderOut: a list of reminders objects
    """

    try:
        qs = Reminder.objects.all().order_by("next_date", "id")
        logToDB(
            "Reminder list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Reminder list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/planning/notes", response=List[NoteOut])
def list_notes(request):
    """
    The function `list_notes` retrieves a list of notes,
    ordered by note date descending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        NoteOut: a list of note objects
    """

    try:
        qs = Note.objects.all().order_by("-note_date")
        logToDB(
            "Note list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Note list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/options", response=List[OptionOut])
def list_options(request):
    """
    The function `list_options` retrieves a list of options,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        OptionOut: a list of option objects
    """

    try:
        qs = Option.objects.all().order_by("id")
        logToDB(
            "Option list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Option list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/transaction/statuses", response=List[TransactionStatusOut])
def list_transaction_statuses(request):
    """
    The function `list_transaction_statuses` retrieves a list of transaction statuses,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        TransactionStatusOut: a list of transaction status objects
    """

    try:
        qs = TransactionStatus.objects.all().order_by("id")
        logToDB(
            "Transaction status list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction status list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/payees", response=List[PayeeOut])
def list_payees(request):
    """
    The function `list_payees` retrieves a list of payees,
    ordered by payee name ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        PayeeOut: a list of payee objects
    """

    try:
        qs = Payee.objects.all().order_by("payee_name")
        logToDB(
            "Payee list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Payee list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/paychecks", response=List[PaycheckOut])
def list_paychecks(request):
    """
    The function `list_paychecks` retrieves a list of paychecks,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        PaycheckOut: a list of paycheck objects
    """

    try:
        qs = Paycheck.objects.all().order_by("id")
        logToDB(
            "Paycheck list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Paycheck list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/transactions", response=PaginatedTransactions)
def list_transactions(
    request,
    account: Optional[int] = Query(None),
    maxdays: Optional[int] = Query(14),
    forecast: Optional[bool] = Query(False),
    page: Optional[int] = Query(1),
    page_size: Optional[int] = Query(60),
):
    """
    The function `list_transactions` retrieves a list of transactions,
    ordered by status, transaction date ascending, custom transaction type,
    and total_amount.
    If this is for a forecast, you can specify the maximum days in the future
    to display transactions from.  If this is not for a forecast, you can specify the
    maxmimum days in the past to view transactions from.  If an account is specified,
    transactions are filtered by that account.  Defaults are no account, 14 days in the past
    and not a forecast.

    Args:
        request (HttpRequest): The HTTP request object.
        account (int): Optional account to filter transactions by.
        maxdays (int): Optional days in the past if not a forecast, days in the future
            if a forecast, default is 14.
        forecast (bool): Optional boolean wether this request is a forecast or not.

    Returns:
        TransactionOut: a list of transaction objects
    """

    try:

        # If an account is specified, filter transactions for maximum days and transaction
        # details that match account
        if account is not None:
            qs = None
            query = None
            today = timezone.now()
            tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
            today_tz = today.astimezone(tz_timezone).date()
            threshold_date = today_tz + timedelta(days=maxdays)
            if forecast is False:
                query = sort_transactions(
                    Transaction.objects.filter(
                        account_id=account,
                        transaction_date__lt=threshold_date,
                    ),
                    False,
                )
            else:
                query = sort_transactions(
                    Transaction.objects.filter(
                        account_id=account,
                        transaction_date__range=(
                            today_tz,
                            threshold_date,
                        ),
                    )
                )
            total_pages = 0
            if page_size is not None and page is not None:
                paginator = Paginator(query, page_size)
                page_obj = paginator.page(page)
                qs = list(page_obj.object_list)
                total_pages = paginator.num_pages
            else:
                qs = query
            total_records = len(query)
            # Initialize blank list of transactions
            transactions = []

            # Calculate the running account balance
            balance = Decimal(0)
            for transaction in qs:

                # Initialize transaction details
                pretty_account = ""
                tags = []
                source_account_name = None
                destination_account_name = None
                account_name = None

                # Get account info
                if transaction.source_account_id:
                    if Account.objects.get(id=transaction.source_account_id):
                        source_account_name = Account.objects.get(
                            id=transaction.source_account_id
                        ).account_name
                    else:
                        source_account_name = "Deleted Account"
                if transaction.destination_account_id:
                    if Account.objects.get(
                        id=transaction.destination_account_id
                    ):
                        destination_account_name = Account.objects.get(
                            id=transaction.destination_account_id
                        ).account_name
                    else:
                        destination_account_name = "Deleted Account"
                if transaction.account_id:
                    if Account.objects.get(id=transaction.account_id):
                        account_name = Account.objects.get(
                            id=transaction.account_id
                        ).account_name
                    else:
                        account_name = "Deleted Account"

                # Retrieve a list of transaction details for the transaction
                transaction_details = TransactionDetail.objects.filter(
                    transaction=transaction.id
                )

                # Process each detail for this transaction
                for detail in transaction_details:

                    # If a tag doesn't already exist in the tags list, add it
                    if detail.tag.tag_name not in tags:
                        tags.append(detail.tag.tag_name)

                if transaction.transaction_type.id == 3:
                    pretty_account = (
                        source_account_name + " => " + destination_account_name
                    )
                else:
                    pretty_account = account_name
                balance = transaction.running_total

                # Update the balance in the transaction and append to the list
                transaction.balance = balance
                transaction.pretty_account = pretty_account
                transaction.tags = tags
                transaction.pretty_total = transaction.total_amount
                transaction.details = transaction_details
                transaction.source_account_id = transaction.source_account_id
                transaction.destination_account_id = (
                    transaction.destination_account_id
                )
                transactions.append(TransactionOut.from_orm(transaction))
            paginated_obj = PaginatedTransactions(
                transactions=transactions,
                current_page=page,
                total_pages=total_pages,
                total_records=total_records,
            )
            return paginated_obj

        # If an account was not specified, these should be upcoming transactions
        else:

            # Filter transactions for pending status and no reminders
            processed_transactions = []
            qs = Transaction.objects.filter(status_id=1, reminder__isnull=True)

            # Set order of transactions
            qs = sort_transactions(qs)
            qs = qs[:10]
            for transaction in qs:

                # Initialize transaction details
                tags = []
                pretty_account = ""
                source_account_name = None
                destination_account_name = None
                account_name = None

                # Get account info
                if transaction.source_account_id:
                    if Account.objects.get(id=transaction.source_account_id):
                        source_account_name = Account.objects.get(
                            id=transaction.source_account_id
                        ).account_name
                    else:
                        source_account_name = "Deleted Account"
                if transaction.destination_account_id:
                    if Account.objects.get(
                        id=transaction.destination_account_id
                    ):
                        destination_account_name = Account.objects.get(
                            id=transaction.destination_account_id
                        ).account_name
                    else:
                        destination_account_name = "Deleted Account"
                if transaction.account_id:
                    if Account.objects.get(id=transaction.account_id):
                        account_name = Account.objects.get(
                            id=transaction.account_id
                        ).account_name
                    else:
                        account_name = "Deleted Account"

                # Retrieve transaction details
                transaction_details = TransactionDetail.objects.filter(
                    transaction=transaction.id
                )

                # Process the details for this transaction
                for detail in transaction_details:

                    # If a tag doesn't already exist in the tags list, add it
                    if detail.tag.tag_name not in tags:
                        tags.append(detail.tag.tag_name)

                if transaction.transaction_type.id == 3:
                    pretty_account = (
                        source_account_name + " => " + destination_account_name
                    )
                else:
                    pretty_account = account_name
                transaction.tags = tags
                transaction.pretty_account = pretty_account
                transaction.pretty_total = transaction.total_amount
                processed_transactions.append(transaction)

            paginated_obj = PaginatedTransactions(
                transactions=processed_transactions,
                current_page=1,
                total_pages=1,
                total_records=len(qs),
            )
            return paginated_obj
        logToDB(
            "Transaction list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/transactions/details", response=List[TransactionDetailOut])
def list_transactiondetails(request):
    """
    The function `list_transactiondetails` retrieves a list of transaction details,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        TransactionDetailOut: a list of transaction detail objects
    """

    try:
        qs = TransactionDetail.objects.all().order_by("id")
        logToDB(
            "Transaction detail list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction detail list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/logentries", response=List[LogEntryOut])
def list_log_entries(request, log_level: Optional[int] = Query(0)):
    """
    The function `list_log_entries` retrieves a list of log entries,
    ordered by id ascending and filtered by log level id.

    Args:
        request (HttpRequest): The HTTP request object.
        log_level (int): Optional log level to filter by, default is 0.

    Returns:
        LogEntryOut: a list of log entry objects
    """

    try:
        qs = LogEntry.objects.filter(error_level__id__gte=log_level).order_by(
            "-id"
        )
        logToDB(
            "Log entry list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Log entry list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/messages", response=MessageList)
def list_messages(request):
    """
    The function `list_messages` retrieves a list of messages,
    ordered by id descending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        MessageList: a message list object that includes unread and totals.
    """

    try:
        unread = Message.objects.filter(
            unread=True
        ).count()  # Total unread messages
        total = Message.objects.all().count()  # The total number of messages
        messages = Message.objects.all().order_by("-id")
        message_list = []
        for message in messages:
            message_list.append(MessageOut.from_orm(message))
        message_list_object = MessageList(
            unread_count=unread, total_count=total, messages=message_list
        )
        logToDB(
            "Message list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return message_list_object
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Message list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.get("/tagtypes", response=List[TagTypeOut])
def list_tag_types(request):
    """
    The function `list_tag_types` retrieves a list of tag types,
    ordered by id ascending and excluding Misc. tags (id=3)

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        TagTypeOut: a list of tag type objects
    """

    try:
        qs = TagType.objects.exclude(id=3).order_by("id")
        logToDB(
            "Tag type list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Tag type list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.put("/accounts/types/{accounttype_id}")
def update_account_type(request, accounttype_id: int, payload: AccountTypeIn):
    """
    The function `update_account_type` updates the account type specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        accounttype_id (int): the id of the account type to update
        payload (AccountTypeIn): an account type object

    Returns:
        success: True

    Raises:
        Http404: If the account type with the specified ID does not exist.
    """

    try:
        account_type = get_object_or_404(AccountType, id=accounttype_id)
        account_type.account_type = payload.account_type
        account_type.color = payload.color
        account_type.icon = payload.icon
        account_type.save()
        logToDB(
            f"Account type updated : {account_type.account_type}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Account type not updated : account type exists ({payload.account_type})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Account type already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Account type not updated : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account type not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/accounts/banks/{bank_id}")
def update_bank(request, bank_id: int, payload: BankIn):
    """
    The function `update_bank` updates the bank specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        bank_id (int): the id of the bank to update
        payload (BankIn): a bank object

    Returns:
        success: True

    Raises:
        Http404: If the bank with the specified ID does not exist.
    """

    try:
        bank = get_object_or_404(Bank, id=bank_id)
        bank.bank_name = payload.bank_name
        bank.save()
        logToDB(
            f"Bank updated : {bank.bank_name}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Bank not updated : bank exists ({payload.bank_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Bank already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Bank not updated : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Bank not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.patch("/accounts/{account_id}")
def update_account(request, account_id: int, payload: AccountUpdate):
    """
    The function `update_account` updates the account specified by id,
    patching the account if a field is sent in the payload.

    Args:
        request (HttpRequest): The HTTP request object.
        account_id (int): the id of the account to update
        payload (AccountUpdate): an account update object

    Returns:
        success: True

    Raises:
        Http404: If the account with the specified ID does not exist.
    """

    try:
        account = get_object_or_404(Account, id=account_id)
        if payload.account_name is not None:
            account.account_name = payload.account_name
        if payload.account_type_id is not None:
            account.account_type_id = payload.account_type_id
        if payload.opening_balance is not None:
            account.opening_balance = payload.opening_balance
        if payload.apy is not None:
            account.apy = payload.apy
        if payload.due_date is not None:
            account.due_date = payload.due_date
        if payload.active is not None:
            account.active = payload.active
        if payload.open_date is not None:
            account.open_date = payload.open_date
        if payload.next_cycle_date is not None:
            account.next_cycle_date = payload.next_cycle_date
        if payload.statement_cycle_length is not None:
            account.statement_cycle_length = payload.statement_cycle_length
        if payload.statement_cycle_period is not None:
            account.statement_cycle_period = payload.statement_cycle_period
        if payload.rewards_amount is not None:
            account.rewards_amount = payload.rewards_amount
        if payload.credit_limit is not None:
            account.credit_limit = payload.credit_limit
        if payload.bank_id is not None:
            account.bank_id = payload.bank_id
        if payload.last_statement_amount is not None:
            account.last_statement_amount = payload.last_statement_amount
        account.save()
        logToDB(
            f"Account updated : {account.account_name}",
            account_id,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Account not updated : account exists ({payload.account_name})",
                account_id,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Account already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Account not updated : db integrity error",
                account_id,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account not updated : {str(e)}",
            account_id,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/tags/{tag_id}")
def update_tag(request, tag_id: int, payload: TagIn):
    """
    The function `update_tag` updates the tag specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        tag_id (int): the id of the tag to update
        payload (TagIn): a tag object

    Returns:
        success: True

    Raises:
        Http404: If the tag with the specified ID does not exist.
    """

    try:
        tag = get_object_or_404(Tag, id=tag_id)
        tag.tag_name = payload.tag_name
        tag.parent_id = payload.parent_id
        tag.tag_type_id = payload.tag_type_id
        tag.save()
        logToDB(
            f"Tag updated : {tag.tag_name}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Tag not updated : tag exists ({payload.tag_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Tag already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Tag not updated : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Tag not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/planning/contribrules/{contribrule_id}")
def update_contrib_rule(request, contribrule_id: int, payload: ContribRuleIn):
    """
    The function `update_contrib_rule` updates the contribution rule specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        contribrule_id (int): the id of the contribution rule to update
        payload (ContribRuleIn): a contribution rule object

    Returns:
        success: True

    Raises:
        Http404: If the contribution rule with the specified ID does not exist.
    """

    try:
        contrib_rule = get_object_or_404(ContribRule, id=contribrule_id)
        contrib_rule.rule = payload.rule
        contrib_rule.cap = payload.cap
        contrib_rule.save()
        logToDB(
            f"Contribution rule updated : {contrib_rule.rule}",
            None,
            None,
            None,
            3001002,
            2,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Contribution rule not updated : contribution rule exists ({payload.rule})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Contribution rule already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Contribution rule not updated : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution rule not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/planning/contributions/{contribution_id}")
def update_contribution(request, contribution_id: int, payload: ContributionIn):
    """
    The function `update_contribution` updates the contribution specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        contribution_id (int): the id of the contribution to update
        payload (ContributionIn): a contribution object

    Returns:
        success: True

    Raises:
        Http404: If the contribution with the specified ID does not exist.
    """

    try:
        contribution = get_object_or_404(Contribution, id=contribution_id)
        contribution.contribution = payload.contribution
        contribution.per_paycheck = payload.per_paycheck
        contribution.emergency_amt = payload.emergency_amt
        contribution.emergency_diff = payload.emergency_diff
        contribution.cap = payload.cap
        contribution.active = payload.active
        contribution.save()
        logToDB(
            f"Contribution updated : {contribution.contribution}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Contribution not updated : contribution exists ({payload.contribution})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Contribution already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Contribution not updated : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/errorlevels/{errorlevel_id}")
def update_errorlevel(request, errorlevel_id: int, payload: ErrorLevelIn):
    """
    The function `update_errorlevel` updates the error level specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        errorlevel_id (int): the id of the error level to update
        payload (ErrorLevelIn): an error level object

    Returns:
        success: True

    Raises:
        Http404: If the error level with the specified ID does not exist.
    """

    try:
        errorlevel = get_object_or_404(ErrorLevel, id=errorlevel_id)
        errorlevel.error_level = payload.error_level
        errorlevel.save()
        logToDB(
            f"Error level updated : {errorlevel.error_level}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Error level not updated : error level exists ({payload.error_level})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Error level already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Error level not updated : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Error level not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/transaction/types/{transaction_type_id}")
def update_transaction_type(
    request, transaction_type_id: int, payload: TransactionTypeIn
):
    """
    The function `update_transaction_type` updates the transaction type specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        transactiontype_id (int): the id of the transaction type to update
        payload (TransactionTypeIn): a transaction type object

    Returns:
        success: True

    Raises:
        Http404: If the transaction type with the specified ID does not exist.
    """

    try:
        transaction_type = get_object_or_404(
            TransactionType, id=transaction_type_id
        )
        transaction_type.transaction_type = payload.transaction_type
        transaction_type.save()
        logToDB(
            f"Transaction type updated : {transaction_type.transaction_type}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Transaction type not updated : transaction type exists ({payload.transaction_type})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Transaction type already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Transaction type not updated : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction type not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/reminders/repeats/{repeat_id}")
def update_repeat(request, repeat_id: int, payload: RepeatIn):
    """
    The function `update_repeat` updates the repeat specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        repeat_id (int): the id of repeat to update
        payload (RepeatIn): a repeat object

    Returns:
        success: True

    Raises:
        Http404: If the repeat with the specified ID does not exist.
    """

    try:
        repeat = get_object_or_404(Repeat, id=repeat_id)
        repeat.repeat_name = payload.repeat_name
        repeat.days = payload.days
        repeat.weeks = payload.weeks
        repeat.months = payload.months
        repeat.years = payload.years
        repeat.save()
        logToDB(
            f"Repeat updated : {repeat.repeat_name}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Repeat not updated : repeat exists ({payload.repeat_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Repeat already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Repeat not updated : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Repeat not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/reminders/{reminder_id}")
def update_reminder(request, reminder_id: int, payload: ReminderIn):
    """
    The function `update_reminder` updates the reminder specified by id.
    Related transactions are deleted and recreated.

    Args:
        request (HttpRequest): The HTTP request object.
        reminder_id (int): the id of the reminder to update
        payload (ReminderIn): a reminder object

    Returns:
        success: True

    Raises:
        Http404: If the reminder with the specified ID does not exist.
    """

    try:
        reminder = get_object_or_404(Reminder, id=reminder_id)
        reminder.tag_id = payload.tag_id
        reminder.amount = payload.amount
        reminder.reminder_source_account_id = payload.reminder_source_account_id
        reminder.reminder_destination_account_id = (
            payload.reminder_destination_account_id
        )
        reminder.description = payload.description
        reminder.transaction_type_id = payload.transaction_type_id
        reminder.start_date = payload.start_date
        reminder.next_date = payload.next_date
        reminder.end_date = payload.end_date
        reminder.repeat_id = payload.repeat_id
        reminder.auto_add = payload.auto_add
        reminder.save()
        reminder_trans_update(reminder_id)
        logToDB(
            f"Reminder updated : #{reminder_id}",
            None,
            reminder_id,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Reminder not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/planning/notes/{note_id}")
def update_note(request, note_id: int, payload: NoteIn):
    """
    The function `update_note` updates the note specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        note_id (int): the id of the note to update
        payload (NoteIn): a note object

    Returns:
        success: True

    Raises:
        Http404: If the note with the specified ID does not exist.
    """

    try:
        note = get_object_or_404(Note, id=note_id)
        note.note_text = payload.note_text
        note.note_date = payload.note_date
        note.save()
        logToDB(
            f"Note updated : #{note_id}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Note not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.patch("/options/{option_id}")
def update_option(request, option_id: int, payload: OptionIn):
    """
    The function `update_option` updates the option specified by id,
    patching the option if a field is sent in the payload.

    Args:
        request (HttpRequest): The HTTP request object.
        option_id (int): the id of the option to update
        payload (OptionIn): an option object

    Returns:
        success: True

    Raises:
        Http404: If the option with the specified ID does not exist.
    """

    try:
        option = get_object_or_404(Option, id=option_id)
        if payload.log_level_id is not None:
            option.log_level_id = payload.log_level_id
        if payload.alert_balance is not None:
            option.alert_balance = payload.alert_balance
        if payload.alert_period is not None:
            option.alert_period = payload.alert_period
        if payload.widget1_graph_name is not None:
            option.widget1_graph_name = payload.widget1_graph_name
        if payload.widget1_tag_id is not None:
            option.widget1_tag_id = payload.widget1_tag_id
        if payload.widget1_expense is not None:
            option.widget1_expense = payload.widget1_expense
        if payload.widget1_month is not None:
            option.widget1_month = payload.widget1_month
        if payload.widget1_exclude is not None:
            option.widget1_exclude = payload.widget1_exclude
        if payload.widget2_graph_name is not None:
            option.widget2_graph_name = payload.widget2_graph_name
        if payload.widget2_tag_id is not None:
            option.widget2_tag_id = payload.widget2_tag_id
        if payload.widget2_expense is not None:
            option.widget2_expense = payload.widget2_expense
        if payload.widget2_month is not None:
            option.widget2_month = payload.widget2_month
        if payload.widget2_exclude is not None:
            option.widget2_exclude = payload.widget2_exclude
        if payload.widget3_graph_name is not None:
            option.widget3_graph_name = payload.widget3_graph_name
        if payload.widget3_tag_id is not None:
            option.widget3_tag_id = payload.widget3_tag_id
        if payload.widget3_expense is not None:
            option.widget3_expense = payload.widget3_expense
        if payload.widget3_month is not None:
            option.widget3_month = payload.widget3_month
        if payload.widget3_exclude is not None:
            option.widget3_exclude = payload.widget3_exclude
        option.save()
        logToDB(
            f"Option updated : {option_id}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Option not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/transaction/statuses/{transactionstatus_id}")
def update_transaction_status(
    request, transactionstatus_id: int, payload: TransactionStatusIn
):
    """
    The function `update_transaction_status` updates the transaction status specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        transactionsatus_id (int): the id of the transaction status to update
        payload (TransactionStatusIn): a transaction status object

    Returns:
        success: True

    Raises:
        Http404: If the transaction status with the specified ID does not exist.
    """

    try:
        transaction_status = get_object_or_404(
            TransactionStatus, id=transactionstatus_id
        )
        transaction_status.transaction_status = payload.transaction_status
        transaction_status.save()
        logToDB(
            f"Transaction status updated : {transaction_status.transaction_status}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Transaction status not updated : transaction status exists ({payload.transaction_status})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Transaction status already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Transaction status not updated : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction status not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/payees/{payee_id}")
def update_payee(request, payee_id: int, payload: PayeeIn):
    """
    The function `update_payee` updates the payee specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        payee_id (int): the id of the payee to update
        payload (NoteIn): a note object

    Returns:
        success: True

    Raises:
        Http404: If the payee with the specified ID does not exist.
    """

    try:
        payee = get_object_or_404(Payee, id=payee_id)
        payee.payee_name = payload.payee_name
        payee.save()
        logToDB(
            f"Payee updated : {payee.payee_name}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Payee not updated : payee exists ({payload.payee_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Payee already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Payee not updated : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Payee not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/paychecks/{paycheck_id}")
def update_paycheck(request, paycheck_id: int, payload: PaycheckIn):
    """
    The function `update_paycheck` updates the paycheck specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        paycheck_id (int): the id of the paycheck to update
        payload (PaycheckIn): a paycheck object

    Returns:
        success: True

    Raises:
        Http404: If the paycheck with the specified ID does not exist.
    """

    try:
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
        logToDB(
            f"Paycheck updated : #{paycheck_id}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Paycheck not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/transactions/{transaction_id}")
def update_transaction(request, transaction_id: int, payload: TransactionIn):
    """
    The function `update_transaction` updates the transaction specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        transaction_id (int): the id of the transaction to update
        payload (TransactionIn): a transaction object

    Returns:
        success: True

    Raises:
        Http404: If the transaction with the specified ID does not exist.
    """

    try:
        # Setup variables
        today = get_today_formatted()
        paycheck = None
        reminder_to_delete = None

        # Get the transaction to update
        transaction = get_object_or_404(Transaction, id=transaction_id)

        if payload.transaction_type_id == 3:
            try:
                # Update Transaction and details
                if transaction.related_transaction:
                    if transaction.id < transaction.related_transaction.id:
                        transaction.total_amount = -abs(payload.total_amount)
                        transaction.account_id = payload.source_account_id
                        detail = TransactionDetail.objects.filter(
                            transaction_id=transaction.id
                        ).first()
                        detail.account_id = payload.source_account_id
                        detail.detail_amt = -abs(payload.total_amount)
                        detail.save()
                    else:
                        transaction.total_amount = abs(payload.total_amount)
                        transaction.account_id = payload.destination_account_id
                        detail = TransactionDetail.objects.filter(
                            transaction_id=transaction.id
                        ).first()
                        detail.account_id = payload.destination_account_id
                        detail.detail_amt = abs(payload.total_amount)
                        detail.save()
                transaction.transaction_date = payload.transaction_date
                transaction.status_id = payload.status_id
                transaction.memo = payload.memo
                transaction.description = payload.description
                transaction.edit_date = today
                transaction.source_account_id = payload.source_account_id
                transaction.destination_account_id = (
                    payload.destination_account_id
                )
                transaction.save()
                logToDB(
                    f"Transaction updated : {transaction_id}",
                    None,
                    None,
                    transaction_id,
                    3001002,
                    1,
                )
                return {"success": True}
            except Exception as e:
                logToDB(
                    f"Transaction not updated : {e}",
                    None,
                    None,
                    transaction_id,
                    3001902,
                    2,
                )
                return {"success": False}
        else:
            # Get Details
            existing_details = TransactionDetail.objects.filter(
                transaction_id=transaction_id
            )
            existing_details.delete()
            for detail in payload.details:
                adj_amount = 0
                if payload.transaction_type_id == 1:
                    adj_amount = -detail.tag_amt
                else:
                    adj_amount = detail.tag_amt
                TransactionDetail.objects.create(
                    transaction_id=transaction_id,
                    account_id=payload.source_account_id,
                    detail_amt=adj_amount,
                    tag_id=detail.tag_id,
                )
                logToDB(
                    "Transaction detail created",
                    None,
                    None,
                    transaction_id,
                    3001001,
                    1,
                )

        # Get existing paycheck if it exists
        if transaction.paycheck_id is not None:
            paycheck = get_object_or_404(Paycheck, id=transaction.paycheck_id)

        # Update existing paycheck
        if payload.paycheck is not None and paycheck is not None:
            paycheck.gross = payload.paycheck.gross
            paycheck.net = payload.paycheck.net
            paycheck.taxes = payload.paycheck.taxes
            paycheck.health = payload.paycheck.health
            paycheck.pension = payload.paycheck.pension
            paycheck.fsa = payload.paycheck.fsa
            paycheck.dca = payload.paycheck.dca
            paycheck.union_dues = payload.paycheck.union_dues
            paycheck.four_fifty_seven_b = payload.paycheck.four_fifty_seven_b
            paycheck.payee_id = payload.paycheck.payee_id
            paycheck.save()
            logToDB(
                "Paycheck updated",
                None,
                None,
                transaction_id,
                3001002,
                1,
            )

        # Create new paycheck
        if payload.paycheck is not None and paycheck is None:
            paycheck = Paycheck.objects.create(
                gross=payload.paycheck.gross,
                net=payload.paycheck.net,
                taxes=payload.paycheck.taxes,
                health=payload.paycheck.health,
                pension=payload.paycheck.pension,
                fsa=payload.paycheck.fsa,
                dca=payload.paycheck.dca,
                union_dues=payload.paycheck.union_dues,
                four_fifty_seven_b=payload.paycheck.four_fifty_seven_b,
                payee_id=payload.paycheck.payee_id,
            )
            logToDB(
                "Paycheck created",
                None,
                None,
                transaction_id,
                3001001,
                1,
            )

        # Delete existing paycheck if no paycheck info passed
        if payload.paycheck is None and paycheck is not None:
            paycheck.delete()
        logToDB(
            "Paycheck deleted",
            None,
            None,
            transaction_id,
            3001003,
            1,
        )

        # Update Reminder
        if transaction.reminder is not None:
            reminder = get_object_or_404(Reminder, id=transaction.reminder_id)
            new_date = transaction.transaction_date
            new_date += relativedelta(days=reminder.repeat.days)
            new_date += relativedelta(weeks=reminder.repeat.weeks)
            new_date += relativedelta(months=reminder.repeat.months)
            new_date += relativedelta(years=reminder.repeat.years)
            prev_date = transaction.transaction_date
            prev_date -= relativedelta(days=reminder.repeat.days)
            prev_date -= relativedelta(weeks=reminder.repeat.weeks)
            prev_date -= relativedelta(months=reminder.repeat.months)
            prev_date -= relativedelta(years=reminder.repeat.years)

            # If transaction date is equal to start date, modify start/next date
            if transaction.transaction_date == reminder.next_date:
                if (
                    reminder.end_date is not None
                    and new_date <= reminder.end_date
                ) or reminder.end_date is None:
                    reminder.next_date = new_date
                    reminder.start_date = new_date
                    transaction.reminder_id = None
                else:
                    transaction.reminder_id = None
                    reminder_to_delete = reminder.id

            # If transaction date is greater than start date, less then end date
            # modify original start/next date, create new reminder
            if transaction.transaction_date > reminder.next_date:
                new_reminder = Reminder.objects.create(
                    tag=reminder.tag,
                    amount=reminder.amount,
                    reminder_source_account=reminder.reminder_source_account,
                    reminder_destination_account=reminder.reminder_destination_account,
                    description=reminder.description,
                    transaction_type=reminder.transaction_type,
                    start_date=reminder.start_date,
                    next_date=reminder.next_date,
                    end_date=prev_date,
                    repeat=reminder.repeat,
                    auto_add=reminder.auto_add,
                )
                trans_to_update_reminders = Transaction.objects.filter(
                    reminder_id=reminder.id, transaction_date__lte=prev_date
                )
                for trans in trans_to_update_reminders:
                    trans.reminder_id = new_reminder.id
                    trans.save()
                    logToDB(
                        "Transaction updated",
                        None,
                        None,
                        trans.id,
                        3001002,
                        1,
                    )
                logToDB(
                    "Reminder created",
                    None,
                    new_reminder.id,
                    None,
                    3001001,
                    1,
                )
                transaction.reminder_id = None
                if reminder.end_date is not None:
                    if new_date <= reminder.end_date:
                        reminder.next_date = new_date
                        reminder.start_date = new_date
                    else:
                        reminder_to_delete = reminder.id
                else:
                    reminder.next_date = new_date
                    reminder.start_date = new_date

            # Save changes to Reminder
            reminder.save()
            logToDB(
                "Reminder updated",
                None,
                reminder.id,
                None,
                3001002,
                1,
            )
        # Update the transaction
        transaction.transaction_date = payload.transaction_date
        transaction.total_amount = payload.total_amount
        transaction.status_id = payload.status_id
        transaction.memo = payload.memo
        transaction.description = payload.description
        transaction.edit_date = today
        transaction.account_id = payload.source_account_id
        transaction.source_account_id = payload.source_account_id
        transaction.destination_account_id = payload.destination_account_id
        if paycheck is not None:
            transaction.paycheck_id = paycheck.id
        else:
            transaction.paycheck_id = None
        transaction.save()
        logToDB(
            f"Transaction updated : {transaction_id}",
            None,
            None,
            transaction_id,
            3001002,
            1,
        )

        # Delete reminder
        if reminder_to_delete is not None:
            get_object_or_404(Reminder, id=reminder_to_delete).delete()
            logToDB(
                f"Reminder deleted: #{reminder_to_delete}",
                None,
                None,
                None,
                3001003,
                1,
            )

        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction not updated : {str(e)}",
            None,
            None,
            transaction_id,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.patch("/transactions/clear/{transaction_id}")
def clear_transaction(request, transaction_id: int, payload: TransactionClear):
    """
    The function `clear_transaction` changes the status to cleared, edit date to today
    of the transaction specified by id.  Skips transactions with a related Reminder.

    Args:
        request (HttpRequest): The HTTP request object.
        transaction_id (int): the id of the transaction to update
        payload (TransactionClear): a transaction clear object

    Returns:
        success: True

    Raises:
        Http404: If the transaction with the specified ID does not exist.
    """

    try:
        transaction = get_object_or_404(Transaction, id=transaction_id)
        if transaction.reminder is None:
            transaction.status_id = payload.status_id
            transaction.edit_date = payload.edit_date
            transaction.save()
            logToDB(
                f"Transaction cleared : #{transaction_id}",
                None,
                None,
                transaction_id,
                3002005,
                1,
            )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction not cleared : {str(e)}",
            None,
            None,
            transaction_id,
            3002905,
            2,
        )
        raise HttpError(500, "Transaction clear error")


@api.put("/transactions/details/{transactiondetail_id}")
def update_transaction_detail(
    request, transactiondetail_id: int, payload: TransactionDetailIn
):
    """
    The function `update_transaction_detail` updates the transacion detail specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        transactiondetail_id (int): the id of the transaction detail to update
        payload (TransactionDetailIn): a transaction detail object

    Returns:
        success: True

    Raises:
        Http404: If the transaction detail with the specified ID does not exist.
    """

    try:
        transaction_detail = get_object_or_404(
            TransactionDetail, id=transactiondetail_id
        )
        transaction_detail.transaction_id = payload.transaction_id
        transaction_detail.account_id = payload.account_id
        transaction_detail.detail_amt = payload.detail_amt
        transaction_detail.tag_id = payload.tag_id
        transaction_detail.save()
        logToDB(
            f"Transaction detail updated : #{transactiondetail_id}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction detail not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/logentries/{logentry_id}")
def update_log_entry(request, logentry_id: int, payload: LogEntryIn):
    """
    The function `update_log_entry` updates the log entry specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        logentry_id (int): the id of the log entry to update
        payload (LogEntryIn): a log entry object

    Returns:
        success: True

    Raises:
        Http404: If the log entry with the specified ID does not exist.
    """

    try:
        log_entry = get_object_or_404(LogEntry, id=logentry_id)
        log_entry.log_date = payload.log_date
        log_entry.log_entry = payload.log_entry
        log_entry.account_id = payload.account_id
        log_entry.reminder_id = payload.reminder_id
        log_entry.transaction_id = payload.transaction_id
        log_entry.error_num = payload.error_num
        log_entry.error_level_id = payload.error_level_id
        log_entry.save()
        logToDB(
            f"Log entry updated : #{logentry_id}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Log entry not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.put("/messages/{message_id}")
def update_message(request, message_id: int, payload: MessageIn):
    """
    The function `update_message` updates the message specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        message_id (int): the id of the message to update
        payload (MessageIn): a message object

    Returns:
        success: True

    Raises:
        Http404: If the message with the specified ID does not exist.
    """

    try:
        message = get_object_or_404(Message, id=message_id)
        message.message_date = payload.message_date
        message.message = payload.message
        message.unread = payload.unread
        message.save()
        logToDB(
            f"Message updated : {message_id}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"sucess": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Message not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@api.patch("/messages/readall/{message_id}")
def update_messages(request, message_id: int, payload: AllMessage):
    """
    The function `update_messages` marks all messages as read.

    Args:
        request (HttpRequest): The HTTP request object.
        message_id (int): defaults to 0 and is unused
        payload (AllMessage): an all message object

    Returns:
        success: True
    """
    try:
        messages = Message.objects.all()

        for message in messages:
            message.unread = payload.unread
            message.save()
        logToDB(
            "All messages marked as read",
            None,
            None,
            None,
            3002006,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Messages not marked as read : {str(e)}",
            None,
            None,
            None,
            3002906,
            2,
        )
        raise HttpError(500, "Messages not marked read error")


@api.delete("/accounts/types/{accounttype_id}")
def delete_account_type(request, accounttype_id: int):
    """
    The function `delete_account_type` deletes the account type specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        accounttype_id (int): the id of the account type to delete

    Returns:
        success: True

    Raises:
        Http404: If the account type with the specified ID does not exist.
    """

    try:
        account_type = get_object_or_404(AccountType, id=accounttype_id)
        account_type_name = account_type.account_type
        account_type.delete()
        logToDB(
            f"Account type deleted : {account_type_name}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account type not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/accounts/banks/{bank_id}")
def delete_bank(request, bank_id: int):
    """
    The function `delete_bank` deletes the bank specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        bank_id (int): the id of the bank to delete

    Returns:
        success: True

    Raises:
        Http404: If the bank with the specified ID does not exist.
    """

    try:
        bank = get_object_or_404(Bank, id=bank_id)
        bank_name = bank.bank_name
        bank.delete()
        logToDB(
            f"Bank deleted : {bank_name}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Bank not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/accounts/{account_id}")
def delete_account(request, account_id: int):
    """
    The function `delete_account` deletes the account specified by id,
    and any related transaction details and transactions.

    Args:
        request (HttpRequest): The HTTP request object.
        account_id (int): the id of the account to delete

    Returns:
        success: True

    Raises:
        Http404: If the account with the specified ID does not exist.
    """

    try:
        # Retrieve the account
        account = get_object_or_404(Account, id=account_id)

        # Retrieve the related transaction details and delete them, keep a running list
        # of transactions that need to be deleted
        transaction_details = TransactionDetail.objects.filter(account=account)
        transactions_to_delete = []
        for detail in transaction_details:
            transaction = detail.transaction
            detail.delete()
            if not transaction.transactiondetail_set.exists():
                transactions_to_delete.append(transaction)

        # Delete the related transactions
        for transaction in transactions_to_delete:
            transaction.delete()
        account_name = account.account_name
        account.delete()
        logToDB(
            f"Account deleted (and related transactions/details) : {account_name}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/tags/{tag_id}")
def delete_tag(request, tag_id: int):
    """
    The function `delete_tag` deletes the tag specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        tag_id (int): the id of the tag to delete

    Returns:
        success: True

    Raises:
        Http404: If the tag with the specified ID does not exist.
    """

    try:
        tag = get_object_or_404(Tag, id=tag_id)
        tag_name = tag.tag_name
        tag.delete()
        logToDB(
            f"Tag deleted : {tag_name}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Tag not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/planning/contribrules/{contribrule_id}")
def delete_contrib_rule(request, contribrule_id: int):
    """
    The function `delete_contrib_rule` deletes the contribution rule specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        contribrule_id (int): the id of the contribution rule to delete

    Returns:
        success: True

    Raises:
        Http404: If the contribution rule with the specified ID does not exist.
    """

    try:
        contrib_rule = get_object_or_404(ContribRule, id=contribrule_id)
        rule_name = contrib_rule.rule
        contrib_rule.delete()
        logToDB(
            f"Contribtion rule deleted : {rule_name}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution rule not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/planning/contributions/{contribution_id}")
def delete_contribution(request, contribution_id: int):
    """
    The function `delete_contribution` deletes the contribution specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        contribution_id (int): the id of the contribution to delete

    Returns:
        success: True

    Raises:
        Http404: If the contribution with the specified ID does not exist.
    """

    try:
        contribution = get_object_or_404(Contribution, id=contribution_id)
        contribution_name = contribution.contribution
        contribution.delete()
        logToDB(
            f"Contribution deleted : {contribution_name}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Contribution not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/errorlevels/{errorlevel_id}")
def delete_errorlevel(request, errorlevel_id: int):
    """
    The function `delete_errorlevel` deletes the error level specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        errorlevel_id (int): the id of the error level to delete

    Returns:
        success: True

    Raises:
        Http404: If the error level with the specified ID does not exist.
    """

    try:
        errorlevel = get_object_or_404(ErrorLevel, id=errorlevel_id)
        error_name = errorlevel.error_level
        errorlevel.delete()
        logToDB(
            f"Error level deleted : {error_name}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Error level not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/transaction/types/{transaction_type_id}")
def delete_transaction_type(request, transaction_type_id: int):
    """
    The function `delete_transaction_type` deletes the transaction type specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        transaction_type_id (int): the id of the transaction type to delete

    Returns:
        success: True

    Raises:
        Http404: If the transaction type with the specified ID does not exist.
    """

    try:
        transaction_type = get_object_or_404(
            TransactionType, id=transaction_type_id
        )
        transaction_type_name = transaction_type.transaction_type
        transaction_type.delete()
        logToDB(
            f"Transaction type deleted : {transaction_type_name}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction type not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/reminders/repeats/{repeat_id}")
def delete_repeat(request, repeat_id: int):
    """
    The function `delete_repeat` deletes the repeat specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        repeat_id (int): the id of the repeat to delete

    Returns:
        success: True

    Raises:
        Http404: If the repeat with the specified ID does not exist.
    """

    try:
        repeat = get_object_or_404(Repeat, id=repeat_id)
        repeat_name = repeat.repeat_name
        repeat.delete()
        logToDB(
            f"Repeat deleted : {repeat_name}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Repeat not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/reminders/{reminder_id}")
def delete_reminder(request, reminder_id: int):
    """
    The function `delete_reminder` deletes the reminder specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        reminder_id (int): the id of the reminder to delete

    Returns:
        success: True

    Raises:
        Http404: If the reminder with the specified ID does not exist.
    """

    try:
        reminder = get_object_or_404(Reminder, id=reminder_id)
        reminder_description = reminder.description
        transactions = Transaction.objects.filter(reminder=reminder)
        pre_delete.disconnect(update_sort_totals, sender=Transaction)
        transactions.delete()
        pre_delete.connect(update_sort_totals, sender=Transaction)
        update_running_totals(True, False, None)
        reminder.delete()
        logToDB(
            f"Reminder deleted : #{reminder_description}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Reminder not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/planning/notes/{note_id}")
def delete_note(request, note_id: int):
    """
    The function `delete_note` deletes the note specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        note_id (int): the id of the note to delete

    Returns:
        success: True

    Raises:
        Http404: If the note with the specified ID does not exist.
    """

    try:
        note = get_object_or_404(Note, id=note_id)
        note_date = note.note_date
        note.delete()
        logToDB(
            f"Note deleted from {note_date}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Note not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/options/{option_id}")
def delete_option(request, option_id: int):
    """
    The function `delete_option` deletes the option specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        option_id (int): the id of the option to delete

    Returns:
        success: True

    Raises:
        Http404: If the option with the specified ID does not exist.
    """

    try:
        option = get_object_or_404(Option, id=option_id)
        option.delete()
        logToDB(
            f"Option deleted : #{option_id}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Option not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/transaction/statuses/{transactionstatus_id}")
def delete_transaction_status(request, transactionstatus_id: int):
    """
    The function `delete_transaction_status` deletes the transaction status specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        transactionstatus_id (int): the id of the transaction status to delete

    Returns:
        success: True

    Raises:
        Http404: If the transaction status with the specified ID does not exist.
    """

    try:
        transaction_status = get_object_or_404(
            TransactionStatus, id=transactionstatus_id
        )
        transaction_status_name = transaction_status.transaction_status
        transaction_status.delete()
        logToDB(
            f"Transaction status deleted : {transaction_status_name}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction status not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/payees/{payee_id}")
def delete_payee(request, payee_id: int):
    """
    The function `delete_payee` deletes the payee specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        payee_id (int): the id of the payee to delete

    Returns:
        success: True

    Raises:
        Http404: If the payee with the specified ID does not exist.
    """

    try:
        payee = get_object_or_404(Payee, id=payee_id)
        payee_name = payee.payee_name
        payee.delete()
        logToDB(
            f"Payee deleted : {payee_name}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Payee not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/paychecks/{paycheck_id}")
def delete_paycheck(request, paycheck_id: int):
    """
    The function `delete_paycheck` deletes the paycheck specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        paycheck_id (int): the id of the paycheck to delete

    Returns:
        success: True

    Raises:
        Http404: If the paycheck with the specified ID does not exist.
    """

    try:
        paycheck = get_object_or_404(Paycheck, id=paycheck_id)
        paycheck.delete()
        logToDB(
            f"Paycheck deleted : {paycheck_id}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Paycheck not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/transactions/{transaction_id}")
def delete_transaction(request, transaction_id: int):
    """
    The function `delete_transaction` deletes the transaction specified by id,
    but skips any that have a related reminder.

    Args:
        request (HttpRequest): The HTTP request object.
        transaction_id (int): the id of the transaction to delete

    Returns:
        success: True

    Raises:
        Http404: If the transaction with the specified ID does not exist.
    """

    try:
        transaction = get_object_or_404(Transaction, id=transaction_id)
        if transaction.reminder is None:
            transaction.delete()
            logToDB(
                f"Transaction deleted : #{transaction_id}",
                None,
                None,
                None,
                3001003,
                1,
            )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/transactions/details/{transactiondetail_id}")
def delete_transaction_detail(request, transactiondetail_id: int):
    """
    The function `delete_transaction_detail` deletes the transaction detail specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        transactiondetail_id (int): the id of the transaction detail to delete

    Returns:
        success: True

    Raises:
        Http404: If the transaction detail with the specified ID does not exist.
    """

    try:
        transaction_detail = get_object_or_404(
            TransactionDetail, id=transactiondetail_id
        )
        transaction_detail.delete()
        logToDB(
            f"Transaction detail deleted : #{transactiondetail_id}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction detail not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/logentries/{logentry_id}")
def delete_log_entry(request, logentry_id: int):
    """
    The function `delete_log_entry` deletes the log entry specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        logentry_id (int): the id of the log entry to delete

    Returns:
        success: True

    Raises:
        Http404: If the log entry with the specified ID does not exist.
    """

    try:
        log_entry = get_object_or_404(LogEntry, id=logentry_id)
        log_entry.delete()
        logToDB(
            f"Log entry deleted : #{logentry_id}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Log entry not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/messages/{message_id}")
def delete_message(request, message_id: int):
    """
    The function `delete_message` deletes the message specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        message_id (int): the id of the message to delete

    Returns:
        success: True

    Raises:
        Http404: If the message with the specified ID does not exist.
    """

    try:
        message = get_object_or_404(Message, id=message_id)
        message.delete()
        logToDB(
            f"Message deleted : #{message_id}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Message not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.delete("/messages/deleteall/{message_id}")
def delete_messages(request, message_id: int):
    """
    The function `delete_messages` deletes all messages.

    Args:
        request (HttpRequest): The HTTP request object.
        message_id (int): defaults to 0, not used

    Returns:
        success: True
    """

    try:
        messages = Message.objects.all()
        for message in messages:
            message.delete()
        logToDB(
            "All Messages deleted",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"All messages not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@api.post("/upload")
def import_file(
    request,
    payload: MappingDefinition,
    import_file: UploadedFile = File(...),
):
    """
    The function `import_file` uploads an import file and its mapping definition.

    Args:
        request (HttpRequest): The HTTP request object.
        payload (MappingDefinition): the mapping definition for the import
        import_file (File): the import file to upload in csv format

    Returns:
        success: True
    """
    try:
        importedFile = FileImport.objects.create(import_file=import_file)
        for type_mapping in payload.transaction_types:
            TypeMapping.objects.create(
                file_type=type_mapping.file_type,
                type_id=type_mapping.type_id,
                file_import=importedFile,
            )
        for status_mapping in payload.transaction_statuses:
            StatusMapping.objects.create(
                file_status=status_mapping.file_status,
                status_id=status_mapping.status_id,
                file_import=importedFile,
            )
        for account_mapping in payload.accounts:
            AccountMapping.objects.create(
                file_account=account_mapping.file_account,
                account_id=account_mapping.account_id,
                file_import=importedFile,
            )
        for tag_mapping in payload.tags:
            TagMapping.objects.create(
                file_tag=tag_mapping.file_tag,
                tag_id=tag_mapping.tag_id,
                file_import=importedFile,
            )
        for transaction in payload.transactions:
            createTransaction = TransactionImport.objects.create(
                line_id=transaction.line_id,
                transaction_date=transaction.transactionDate,
                transaction_type_id=transaction.transactionTypeID,
                transaction_status_id=transaction.transactionStatusID,
                amount=transaction.amount,
                description=transaction.description,
                source_account_id=transaction.sourceAccountID,
                destination_account_id=transaction.destinationAccountID,
                memo=transaction.memo,
                file_import=importedFile,
            )
            for tag in transaction.tags:
                TransactionImportTag.objects.create(
                    tag_id=tag.tag_id,
                    tag_name=tag.tag_name,
                    tag_amount=tag.tag_amount,
                    transaction_import=createTransaction,
                )
            for error in transaction.errors:
                TransactionImportError.objects.create(
                    text=error.text,
                    status=error.status,
                    transaction_import=createTransaction,
                )
        today = timezone.now()
        tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
        today_tz = today.astimezone(tz_timezone).date()
        Message.objects.create(
            message_date=today_tz,
            message=f"File import ID #{importedFile.id} started",
            unread=True,
        )
        logToDB(
            f"File import ID #{importedFile.id} started",
            None,
            None,
            None,
            3002001,
            2,
        )
        return {"id": importedFile.id}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"File import failed : {str(e)}",
            None,
            None,
            None,
            3002901,
            3,
        )
        raise HttpError(500, "File import error")


# Helper Functions
def reminder_trans_add(reminder_id):
    """
    The function `reminder_trans_add` creates transactions for the specified reminder.

    Args:
        reminder_id (int): The id of the reminder to create transactions from.

    Returns:
        success (bool): Returns true if successful.
    """
    try:
        # Get the reminder object
        reminder = get_object_or_404(Reminder, id=reminder_id)

        # Starting with the start date, create transactions based on repeat
        # until end date

        # Extract reminder details
        start_date = reminder.start_date
        end_date = (
            reminder.end_date
            if reminder.end_date
            else start_date + relativedelta(years=10)
        )  # 10 years from start
        repeat_days = reminder.repeat.days
        repeat_weeks = reminder.repeat.weeks
        repeat_months = reminder.repeat.months
        repeat_years = reminder.repeat.years

        current_date = start_date
        transactions_to_create = []
        tags = []
        tag_obj = CustomTag(
            tag_name=None, tag_amount=reminder.amount, tag_id=reminder.tag.id
        )
        tags.append(tag_obj)
        while current_date <= end_date:
            # Create transaction for current date
            source_account_id = reminder.reminder_source_account.id
            destination_account_id = None
            if reminder.reminder_destination_account:
                destination_account_id = (
                    reminder.reminder_destination_account.id
                )
            transaction = FullTransaction(
                transaction_date=current_date,
                total_amount=reminder.amount,
                status_id=1,
                memo="",
                description=reminder.description,
                edit_date=current_date,
                add_date=current_date,
                transaction_type_id=reminder.transaction_type.id,
                reminder_id=reminder_id,
                paycheck_id=None,
                source_account_id=source_account_id,
                destination_account_id=destination_account_id,
                tags=tags,
            )
            print(f"transaction: {transaction}")
            transactions_to_create.append(transaction)

            # Increment current date based on repeat interval
            current_date += relativedelta(days=repeat_days)
            current_date += relativedelta(weeks=repeat_weeks)
            current_date += relativedelta(months=repeat_months)
            current_date += relativedelta(years=repeat_years)
        create_transactions(transactions_to_create)
        logToDB(
            "Reminder transactions created",
            None,
            reminder_id,
            None,
            3002007,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Unable to create reminder transactions : {str(e)}",
            None,
            reminder_id,
            None,
            3002907,
            3,
        )
        return {"success": False}


def reminder_trans_update(reminder_id):
    """
    The function `reminder_trans_update` deletes and then recreates transactions for the specified reminder.

    Args:
        reminder_id (int): The id of the reminder to update transactions.

    Returns:
        success (bool): Returns true if successful.
    """

    try:
        # Delete the existing reminder transactions
        transactions = Transaction.objects.filter(reminder__id=reminder_id)
        transactions.delete()
        logToDB(
            "Reminder transactions deleted",
            None,
            reminder_id,
            None,
            3002008,
            1,
        )
        reminder_trans_add(reminder_id)
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Unable to update reminder transactions : {str(e)}",
            None,
            reminder_id,
            None,
            3002908,
            3,
        )
