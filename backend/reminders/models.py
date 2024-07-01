from django.db import models
from datetime import date
from django.utils import timezone
from django.db.models import Case, When, Q, Value, IntegerField
from decimal import Decimal
import datetime
from typing import List
from django.db import IntegrityError, connection, transaction
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet
from tags.models import Tag
from accounts.models import Account

# Create your models here.


class Repeat(models.Model):
    """
    Model representing a repeat period for reminders. Defined by setting how many
    days, weeks, months and years are in the repeat period.  Can be combined to create
    a custom repeat period.

    Fields:
    - repeat_name (CharField): The name of the repeat, limited to 254 characters,
    and must be unique.
    - days (IntegerField): The amount of days in this repeat period.
    - weeks (IntegerField): The amount of weeks in this repeat period.
    - months (IntegerField): The amount of months in this repeat period.
    - years (IntegerField): The amount of years in this repeat period.
    """

    repeat_name = models.CharField(max_length=254, unique=True)
    days = models.IntegerField(default=0)
    weeks = models.IntegerField(default=0)
    months = models.IntegerField(default=0)
    years = models.IntegerField(default=0)

    def __str__(self):
        return self.repeat_name


class Reminder(models.Model):
    """
    Model representing a reminder, which is a repeating transaction.

    Fields:
    - tag (ForeignKey): a refemrece to the Tag model, which categories the
    transaction details related to this reminder.
    - reminder_source_account (ForeignKey): a reference to the Account model,
    which represents the source account for transaction details related to this
    reminder.
    - reminder_destination_account (ForeignKey): a reference to the Account model,
    which represents the destination account for transaction details related to this
    reminder.  Can be null and is only used for transfers.
    - description (CharField): the description of transactions related to this reminder,
    limited to 254 characters.
    - transaction_type (ForeignKey): a reference to the TransactionType model, which
    represents the type of transactions related to this reminder.
    - start_date (DateField): the date reminder transactions start for this reminder,
    defaults to today.
    - next_date (DateField): the date of the next transaction associated with this reminder,
    can be null.
    - end_date (DateField): the last date of transactions associated with this reminder, can
    be null if this reminder has no end.
    - repeat (ForeignKey): a reference to the Repeat model, representing the repeat period
    that this reminder follows.
    - auto_add (BooleanField): whether the system auto adds the transactions, default is false.
    """

    tag = models.ForeignKey(
        Tag, on_delete=models.SET_NULL, null=True, blank=True
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    reminder_source_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reminder_source_account",
    )
    reminder_destination_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reminder_destination_account",
    )
    description = models.CharField(max_length=254)
    transaction_type = models.ForeignKey(
        "transactions.TransactionType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    start_date = models.DateField(default=timezone.now().date)
    next_date = models.DateField(default=None, null=True, blank=True)
    end_date = models.DateField(default=None, null=True, blank=True)
    repeat = models.ForeignKey(
        Repeat, on_delete=models.SET_NULL, null=True, blank=True
    )
    auto_add = models.BooleanField(default=False)

    def __str__(self):
        return self.description
