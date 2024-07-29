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
from tags.models import Tag, TagType, MainTag, SubTag
from reminders.models import Repeat, Reminder, ReminderExclusion
from planning.models import ChristmasGift, ContribRule, Contribution, Note
from administration.models import (
    ErrorLevel,
    LogEntry,
    Message,
    Option,
    Payee,
    logToDB,
)
from typing import List, Optional, Dict, Any
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
    Subquery,
    OuterRef,
    FloatField,
    Window,
    ExpressionWrapper,
    DecimalField,
    Func,
    Count,
)
from django.db import models, IntegrityError
from django.db.models.functions import Concat, Coalesce, Abs
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import random
import json
from django.core.paginator import Paginator
from django.db.models.signals import pre_delete, post_delete
import pytz
import os
from django.contrib.postgres.aggregates import ArrayAgg
from decimal import Decimal
import traceback
from administration.api.dependencies.get_todays_date_timezone_adjusted import (
    get_todays_date_timezone_adjusted,
)


class Round(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s::numeric, 2)"


# The class TransactionDetailOut is a schema for representing Transaction Details.
class TransactionDetailOut(Schema):
    id: int
    transaction: "TransactionOut"
    detail_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    tag: TagOut


# The class TransactionOut is a schema for representing Transactions.
class TransactionOut(Schema):
    id: int
    transaction_date: date
    total_amount: Decimal = Field(whole_digits=10, decimal_places=2)
    status: TransactionStatusOut
    memo: Optional[str] = None
    description: str
    edit_date: date
    add_date: date
    transaction_type: TransactionTypeOut
    paycheck: Optional[PaycheckOut] = None
    balance: Optional[Decimal] = Field(
        default=None, whole_digits=10, decimal_places=2
    )
    pretty_account: Optional[str]
    tags: Optional[List[Optional[str]]] = []
    details: List[TransactionDetailOut] = []
    pretty_total: Optional[Decimal] = Field(
        default=None, whole_digits=10, decimal_places=2
    )
    source_account_id: Optional[int] = None
    destination_account_id: Optional[int] = None
    checkNumber: Optional[int] = None
    reminder_id: Optional[int] = None


# The class TagTransactionOut is a schema for representing Transactions by Tag.
class TagTransactionOut(Schema):
    transaction: TransactionOut
    detail_amt: Decimal = Field(whole_digits=10, decimal_places=2)
    pretty_account: str
    tag: TagOut


# The class TagGraphOut is a schema for representing a tag bar graph data.
class TagGraphOut(Schema):
    data: GraphData
    year1: int
    year2: int
    year1_avg: Decimal = Field(whole_digits=10, decimal_places=2)
    year2_avg: Decimal = Field(whole_digits=10, decimal_places=2)
    transactions: List[TagTransactionOut]


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
        tags = None

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
            tags = Tag.objects.filter(tag_type__id=tag_type_id).exclude(
                id__in=exclude_list
            )
            # Calculate month totals for each tag
            # Use the tag name as the label and the total as the value
            for tag in tags:
                tag_amount = (
                    TransactionDetail.objects.filter(
                        tag=tag,
                        transaction__transaction_date__month=target_month,
                        transaction__transaction_date__year=target_year,
                        transaction__status__id__gt=1,
                    ).aggregate(Sum("detail_amt"))["detail_amt__sum"]
                    or 0
                )
                if tag_amount != 0:
                    labels.append(tag.tag_name)
                    values.append(tag_amount)
            result = Transaction.objects.filter(
                transaction_date__month=target_month,
                transaction_date__year=target_year,
                status__id__gt=1,
                transaction_type_id=tag_type_id,
            )
            result = result.annotate(tag_count=Count("transactiondetail__id"))
            result = result.filter(tag_count=0)

            result = result.aggregate(total=Sum(F("total_amount")))

            untagged_total = result["total"] or 0
            if untagged_total != 0:
                values.append(untagged_total)
                labels.append("Untagged")
        elif tagID != -1:
            tags = Tag.objects.filter(parent__id=tagID).exclude(
                id__in=exclude_list
            )

            # Calculate month totals for each tag
            # Use the tag name as the label and the total as the value
            for tag in tags:
                tag_amount = (
                    TransactionDetail.objects.filter(
                        tag=tag,
                        transaction__transaction_date__month=target_month,
                        transaction__transaction_date__year=target_year,
                        transaction__status__id__gt=1,
                    ).aggregate(Sum("detail_amt"))["detail_amt__sum"]
                    or 0
                )
                if tag_amount != 0:
                    labels.append(tag.tag_name)
                    values.append(tag_amount)
        elif tagID == -1:
            result = Transaction.objects.filter(
                transaction_date__month=target_month,
                transaction_date__year=target_year,
                status__id__gt=1,
            )
            result = result.annotate(tag_count=Count("transactiondetail__id"))
            result = result.filter(tag_count=0)

            result = result.aggregate(total=Sum(F("total_amount")))

            untagged_total = result["total"] or 0
            values.append(untagged_total)
            labels.append("Untagged")

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
        raise HttpError(500, f"Record retrieval error: {str(e)}")


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
        source_account_name = Account.objects.filter(
            id=OuterRef("transaction__source_account_id")
        ).values("account_name")[:1]
        destination_account_name = Account.objects.filter(
            id=OuterRef("transaction__destination_account_id")
        ).values("account_name")[:1]

        # Retrieve all transactions for tag
        alltrans = TransactionDetail.objects.filter(
            Q(tag__id=tag) & Q(transaction__status__id__gt=1)
        ).order_by("-transaction__transaction_date")

        # Annotate source account names
        alltrans = alltrans.annotate(
            source_name=Coalesce(
                Subquery(source_account_name), Value("Unknown Account")
            )
        )

        # Annotate destination account names
        alltrans = alltrans.annotate(
            destination_name=Coalesce(
                Subquery(destination_account_name), Value("Unknown Account")
            )
        )

        # Annotate pretty account
        alltrans = alltrans.annotate(
            pretty_account=Case(
                When(
                    transaction__transaction_type_id=3,
                    then=Concat(
                        F("source_name"),
                        Value(" => "),
                        F("destination_name"),
                    ),
                ),
                default=F("source_name"),
                output_field=CharField(),  # Correctly specify the output field
            )
        )

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
            transactions=list(alltrans),
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
        raise HttpError(500, f"Record retrieval error: {str(e)}")


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
            # Set end_date
            end_date = get_todays_date_timezone_adjusted() + timedelta(
                days=maxdays
            )

            # Get a complete list of transactions, including reminders, sorted with totals
            all_transactions_list, previous_balance = (
                get_complete_transaction_list_with_totals(
                    end_date, account, False, forecast
                )
            )

            # Reverse transactions if not forecast
            if not forecast:
                reversed_all_transactions_list = list(
                    reversed(all_transactions_list)
                )

            # Paginate transactions
            total_pages = 0
            if page_size is not None and page is not None:
                paginator = None
                if not forecast:
                    paginator = Paginator(
                        reversed_all_transactions_list, page_size
                    )
                else:
                    paginator = Paginator(all_transactions_list, page_size)
                page_obj = paginator.page(page)
                qs = list(page_obj.object_list)
                total_pages = paginator.num_pages
            else:
                qs = past_transactions
            total_records = len(all_transactions_list)
            paginated_obj = PaginatedTransactions(
                transactions=qs,
                current_page=page,
                total_pages=total_pages,
                total_records=total_records,
            )
            return paginated_obj

        # If an account was not specified, these should be upcoming transactions
        else:

            # Setup subqueries
            source_account_name = Account.objects.filter(
                id=OuterRef("source_account_id")
            ).values("account_name")[:1]
            destination_account_name = Account.objects.filter(
                id=OuterRef("destination_account_id")
            ).values("account_name")[:1]
            transaction_detail_subquery = (
                TransactionDetail.objects.filter(
                    transaction_id=OuterRef("id"),
                )
                .annotate(
                    parent_tag=F("tag__parent__tag_name"),
                    child_tag=F("tag__child__tag_name"),
                    tag_name_combined=Case(
                        When(child_tag__isnull=True, then=F("parent_tag")),
                        default=Concat(
                            F("parent_tag"), Value(" / "), F("child_tag")
                        ),
                        output_field=CharField(),
                    ),
                )
                .exclude(tag_name_combined__isnull=True)
                .values_list("tag_name_combined", flat=True)
            )

            # Filter transactions for pending status and no reminders
            qs = Transaction.objects.filter(status_id=1)

            # Set order of transactions
            qs = sort_transactions(qs)
            qs = qs[:10]
            qs = qs.annotate(
                source_name=Coalesce(
                    Subquery(source_account_name),
                    Value("Unknown Account"),
                ),
                destination_name=Coalesce(
                    Subquery(destination_account_name),
                    Value("Unknown Account"),
                ),
            )
            qs = qs.annotate(
                pretty_account=Case(
                    When(
                        transaction_type_id=3,
                        then=Concat(
                            F("source_name"),
                            Value(" => "),
                            F("destination_name"),
                        ),
                    ),
                    default=F("source_name"),
                    output_field=CharField(),  # Correctly specify the output field
                )
            )
            qs = qs.annotate(
                pretty_total=Case(
                    When(
                        transaction_type_id=2,
                        then=Abs(F("total_amount")),
                    ),
                    When(
                        transaction_type_id=1,
                        then=-Abs(F("total_amount")),
                    ),
                    When(
                        transaction_type_id=3,
                        then=-Abs(F("total_amount")),
                    ),
                    default=Value(
                        0,
                        output_field=DecimalField(
                            max_digits=12, decimal_places=2
                        ),
                    ),  # Ensure the correct output field
                    output_field=DecimalField(
                        max_digits=12, decimal_places=2
                    ),  # Ensure the correct output field
                )
            )
            qs = qs.annotate(
                tags=ArrayAgg(
                    Subquery(
                        transaction_detail_subquery.values("tag_name_combined")
                    )
                )
            )
            query = list(qs)
            paginated_obj = PaginatedTransactions(
                transactions=query,
                current_page=1,
                total_pages=1,
                total_records=len(query),
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
        raise HttpError(500, f"Record retrieval error: {str(e)}")


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
        today = get_todays_date_timezone_adjusted()
        paycheck = None

        # Get the transaction to update
        transaction = get_object_or_404(Transaction, id=transaction_id)

        # Get Details
        existing_details = TransactionDetail.objects.filter(
            transaction_id=transaction_id
        )
        existing_details.delete()
        for detail in payload.details:
            adj_amount = 0
            if payload.transaction_type_id == 1:
                adj_amount = -abs(detail.tag_amt)
            else:
                adj_amount = abs(detail.tag_amt)
            TransactionDetail.objects.create(
                transaction_id=transaction_id,
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

        # Update the transaction
        transaction.transaction_date = payload.transaction_date
        transaction.total_amount = payload.total_amount
        transaction.status_id = payload.status_id
        transaction.memo = payload.memo
        transaction.description = payload.description
        transaction.edit_date = today
        transaction.source_account_id = payload.source_account_id
        transaction.destination_account_id = payload.destination_account_id
        transaction.checkNumber = payload.checkNumber
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
