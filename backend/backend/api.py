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
