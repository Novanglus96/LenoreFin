from django.db import models
from datetime import date
from django.utils import timezone
from decimal import Decimal
import datetime
from typing import List
from django.db import IntegrityError, connection, transaction
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet
from tags.models import Tag


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


# Create your models here.


class ChristmasGift(models.Model):
    """
    Model representing a christmas gift.

    Fields:
    - budget (DecimalField): The amount to budget to this christmas gift, default is
    0.00.
    - tag (ForeignKey): A reference to Tag model, representing the tag associated with
    this christmas gift.
    """

    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tag = models.ForeignKey(Tag, null=True, on_delete=models.SET_NULL)


class ContribRule(models.Model):
    """
    Model representing a contribution rule describing a rule for extra money each
    paycheck.

    Fields:
    - rule (CharField): The description of the contribution rule, limited to 254 characters.
    - cap (CharField): The cap rule for this contribution rule, lmited to 254 charaters.
    """

    rule = models.CharField(max_length=254, unique=True)
    cap = models.CharField(max_length=254, null=True, blank=True, default=None)

    def __str__(self):
        return self.rule


class Contribution(models.Model):
    """
    Model representing a contribution to be taken out each paycheck.

    Fields:
    - contribution (CharField): The description of the contribution, limited to 254 characters,
    and must be unique.
    - per_paycheck (DecimalField): The amount to deduct per paycheck for this contribution, default
    is 0.00.
    - emergency_amt (DecimalField): The amount that can be diverted in an emergency, per paycheck,
    defult is 0.00.
    - emergency_diff (DecimalField): The amount left in an emergency, per paycheck, default is 0.00.
    - cap (DecimalField): The cap for destination contibution that shuts off this contribution, default
    is 0.00.
    - active (BooleanField): Wether or not this contribution is active.
    """

    contribution = models.CharField(max_length=20, unique=True)
    per_paycheck = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    emergency_amt = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    emergency_diff = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    cap = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.contribution


class Note(models.Model):
    """
    Model representing a note used to add notes relevant to planning.

    Fields:
    - note_text (CharField): The text of the note, limited to 254 characters
    - note_date (DateField): the date this note was added, defaults to today.
    """

    note_text = models.CharField(max_length=254)
    note_date = models.DateField(default=current_date)

    def __str__(self):
        return f"{self.note_date}"


class CalculationRule(models.Model):
    """
    Model representing a caluclation rule used to add amounts to relevant transfers.

    Fields:
    - tag_ids (CharField): A string array of tag ids.
    - name (CharFieldField): A name for this rule
    - source_account_id (int): The ID of the source account for transfers
    - destination_account_id (int): The ID of the destination account for transfers
    """

    tag_ids = models.CharField(max_length=254)
    name = models.CharField(max_length=254, unique=True)
    source_account_id = models.IntegerField()
    destination_account_id = models.IntegerField()
