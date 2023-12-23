from ninja import NinjaAPI, Schema
from api.models import Account, AccountType, CalendarDate, Tag, ChristmasGift, ContribRule, Contribution, ErrorLevel, TransactionType, Repeat, Reminder, Note, Option, TransactionStatus, Transaction, TransactionDetail, LogEntry
from typing import List, Optional
from django.shortcuts import get_object_or_404

api = NinjaAPI()
api.title = "Money API"
api.version = "1.0.0"
api.description = "API documentation for Money"
