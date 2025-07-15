"""
Module: models.py
Description: Contains django model definitions.

Author: John Adams <johnmadams96@gmail.com>
Date: February 15, 2024
"""

from django.db import models
from datetime import date
from django.utils import timezone
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.db.models import Case, When, Q, Value, IntegerField
from decimal import Decimal
import datetime
from typing import List
from django.db import IntegrityError, connection, transaction
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet
from accounts.models import Account
from tags.models import Tag
from administration.models import LogEntry, Option
import pytz
import os


def transaction_image_name(instance, filename):
    timestamp = timezone.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"tran_images/{timestamp}-{filename}"


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


# Create your models here.


class TransactionType(models.Model):
    """
    Model representing a transaction type to determine the type of transaction.

    Fields:
    - transaction_type (CharField): The name of the transaction type, limited to 254 characters,
    and must be unique.
    """

    transaction_type = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.transaction_type


class TransactionStatus(models.Model):
    """
    Model representing a transactions status.

    Fields:
    - transaction_status (CharField): The transaction status, limited to 254 characters
    """

    transaction_status = models.CharField(max_length=254, unique=True)

    class Meta:
        verbose_name_plural = "Transaction statuses"

    def __str__(self):
        return self.transaction_status


class Paycheck(models.Model):
    """
    Model representing a paycheck.

    Fields:
    - gross (DecimalField): The gross amount of the paycheck, default is 0.00.
    - net (DecimalField): The net amount of the paycheck, default is 0.00.
    - taxes (DecimalField): The taxes of the paycheck, default is 0.00.
    - health (DecimalField): The total health deduction of the paycheck, default is 0.00.
    - pension (DecimalField): The pension deduction of the paycheck, default is 0.00.
    - fsa (DecimalField): The FSA deduction of the paycheck, default is 0.00.
    - dca (DecimalField): The DCA deduction of the paycheck, default is 0.00.
    - union_dues (DecimalField): The union dues deduction of the paycheck, default is 0.00.
    - four_fifty_seven_b (DecimalField): The 457b deduction of the paycheck, default is 0.00.
    - payee (ForeignKey): A reference to the Payee model, representing the payee of the paycheck.
    """

    gross = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    taxes = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    health = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    pension = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    fsa = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    dca = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    union_dues = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    four_fifty_seven_b = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    payee = models.ForeignKey(
        "administration.Payee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )


class Transaction(models.Model):
    """
    Model representing a transaction.

    Fields:
    - transaction_date (DateField): The date of the transaction, defaults to today.
    - total_amount (DecimalField): The total amount of the transaction, default is 0.00.
    - status (ForeignKey): A reference to the TransactionStatus model, representing the
    status of the transaction.
    - memo (CharField): A memo to document this transaction, limited to 254 characters.
    - description (CharField): A description of this description, limited to 254 characters.
    - edit_date (DateField): The last date this transacion was edited, defaults to today.
    - add_date (DateField): The date this transaction was added, defaults to today.
    - transaction_type (ForeignKey): A reference to the TransactionType model, representing
    the type of this transaction.
    - paycheck (ForeignKey): A reference to the Paycheck model, representing a paycheck
    associated with this transaction.  Default is None, and is Optional.
    - checkNumber (IntegerField): Number of a check associated with this transaction. Default
    is None, and is Optional.
    - sourceAccount (ForeignKey): A reference to Account model, representing the source account.
    - destinationAccount (ForeignKey): A reference to Account model, representing the destination
    account.
    """

    transaction_date = models.DateField(default=current_date)
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    status = models.ForeignKey(
        TransactionStatus, on_delete=models.SET_NULL, null=True, blank=True
    )
    memo = models.TextField(null=True, blank=True, default=None)
    description = models.CharField(max_length=254)
    edit_date = models.DateField(default=current_date)
    add_date = models.DateField(default=current_date)
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    paycheck = models.ForeignKey(
        Paycheck,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    checkNumber = models.IntegerField(null=True, blank=True, default=None)
    source_account = models.ForeignKey(
        Account,
        related_name="source_transactions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    destination_account = models.ForeignKey(
        Account,
        related_name="destination_transactions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return f"#{self.id} | {self.transaction_date} : {self.description} (${self.total_amount})"


class TransactionImage(models.Model):
    """
    Model representing a transaction image.

    Fields:
    - image (ImageField): The image.
    - transaction (ForeignKey): A reference to the Transaction model, associating the
    transaction with this image.
    """

    image = models.FileField(upload_to=transaction_image_name)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        # Delete the associated file when the instance is deleted
        self.image.delete()
        super().delete(*args, **kwargs)


class TransactionDetail(models.Model):
    """
    Model representing a transaction detail, that combined with an associated
    transaction, represents a full transaction.

    Fields:
    - transaction (ForeignKey): A reference to the Transaction model, representing
    the transaction associated with this transaction detail.
    - detail_amt (DecimalField): The amount associated with this transaction detail,
    default is 0.00.
    - tag (ForeignKey): A refernce to the Tag model, representing the tag category
    ot this transaction detail.
    """

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    detail_amt = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.SET_NULL, null=True, blank=True
    )
    full_toggle = models.BooleanField(default=False)
