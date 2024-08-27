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
import pytz
import os
from django.core.exceptions import ValidationError


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


# Create your models here.


class AccountType(models.Model):
    """
    Model representing an account type for categorizing accounts.

    Fields:
    - account_type (CharField): The name of the account type, limited to 254 characters,
    and must be unique.
    - color (CharField): The color associated with accounts of this type, default is #059669.
    - icon (CharField): The icon associciated with accounts of this type, limited to 25
    characters.
    """

    account_type = models.CharField(max_length=254, unique=True)
    color = models.CharField(max_length=7, default="#059669")
    icon = models.CharField(max_length=25)

    def __str__(self):
        return self.account_type


class Bank(models.Model):
    """
    Model representing a bank to be used for accounts.

    Fields:
    - bank_name (CharField): The name of the bank, limited to 254 characters,
    and must be unique.
    """

    bank_name = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.bank_name


class Account(models.Model):
    """
    Model representing a banking account.

    Fields:
    - account_name (CharField): The name of the account, limited to 254 characters.
    - account_type (ForeignKey): A reference to the AccountType model, representing the type of the account.
    - opening_balance (DecimalField): The initial balance of the account, defaulting to 0.00.
    - apy (DecimalField): The annual percentage yield (APY) of the account, defaulting to 0.00.
    - due_date (DateField): The due date for the account, defaulting to today's date.
    - active (BooleanField): Indicates whether the account is active or not, defaulting to True.
    - open_date (DateField): The date when the account was opened, defaulting to today's date.
    - next_cycle_date (DateField): The date of the next billing cycle for the account, defaulting to today's date.
    - statement_cycle_length (IntegerField): The length of the statement cycle for the account, defaulting to 0.
    - statement_cycle_period (CharField): The period of the statement cycle, defaulting to 'd' (day).
    - rewards_amount (DecimalField): The amount of rewards associated with the account, defaulting to 0.00.
    - credit_limit (DecimalField): The credit limit of the account, defaulting to 0.00.
    - bank (ForeignKey): A reference to the Bank model representing the bank associated with the account.
    - last_statement_amount (DecimalField): The amount of the last statement for the account, defaulting to 0.00.
    - funding_account (ForeignKey): A reference to another Account that funds this account, can be null.
    """

    account_name = models.CharField(max_length=254, unique=True)
    account_type = models.ForeignKey(
        AccountType, null=True, on_delete=models.SET_NULL
    )
    opening_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=True
    )
    apy = models.DecimalField(
        max_digits=4, decimal_places=2, default=0.00, null=True, blank=True
    )
    due_date = models.DateField(default=current_date, null=True, blank=True)
    active = models.BooleanField(default=True)
    open_date = models.DateField(default=current_date, null=True)
    next_cycle_date = models.DateField(
        default=current_date, null=True, blank=True
    )
    statement_cycle_length = models.IntegerField(
        default=0, null=True, blank=True
    )
    statement_cycle_period = models.CharField(
        max_length=1, null=True, default="d", blank=True
    )
    credit_limit = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=True, blank=True
    )
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    last_statement_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=True, blank=True
    )
    archive_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=True, blank=True
    )
    funding_account = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="funded_accounts",
    )

    def clean(self):
        # Ensure an account cannot fund itself
        if self.funding_account and self.funding_account == self:
            raise ValidationError(
                "An account cannot be its own funding account."
            )
        # Ensure the funding account is a checking account
        if self.funding_account and self.funding_account.account_type.id != 2:
            raise ValidationError(
                "A funding account must be a checking account"
            )
        # Ensure the account is a credit card
        if self.funding_account and self.account_type.id != 1:
            raise ValidationError(
                "A funding account can only be set for Credit Card accounts"
            )

    def __str__(self):
        return self.account_name


class Reward(models.Model):
    """
    Model representing a reward to be used for cc accounts.

    Fields:
    - reward_date (Date): The date the award amount was added
    - reward_amount (DecimalField): The amount of the rewards on
    this date
    - reward_account (ForeignKey): The account associated with this
    reward
    """

    reward_date = models.DateField(default=current_date)
    reward_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=True
    )
    reward_account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.reward_date} : {self.reward_account.account_name} (${self.reward_amount})"
