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


# Helper Functions
