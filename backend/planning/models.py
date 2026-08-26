from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from tags.models import Tag
from reminders.models import Repeat
import pytz
import os


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
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.rule


class Contribution(models.Model):
    """
    Model representing a contribution to be taken out each paycheck.

    A contribution ties three things together:
    - the *intent* (`per_paycheck`, and a goal for the funded account),
    - the *account* the money lands in,
    - the *mechanism* (`reminder`) that actually moves it.

    `per_paycheck` is what you plan to contribute; the linked reminder's amount
    is what is actually scheduled. The two can disagree, and the planner surfaces
    that drift rather than silently trusting either one.

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
    - account (ForeignKey): The account this contribution funds. Null until linked.
    - reminder (ForeignKey): The recurring transfer that moves the money. Null until linked.
    - goal_type (CharField): What this account should do — see GOAL_CHOICES.
    - goal_amount (DecimalField): Target balance (TARGET), floor (FLOOR), or growth
      per month in dollars (GROW when goal_rate is 0).
    - goal_date (DateField): The date a TARGET goal must be met by.
    - goal_rate (DecimalField): Annual growth rate as a percent, for GROW goals.
      Takes precedence over goal_amount when non-zero.
    """

    GOAL_NONE = "none"
    GOAL_HOLD = "hold"
    GOAL_TARGET = "target"
    GOAL_FLOOR = "floor"
    GOAL_GROW = "grow"

    GOAL_CHOICES = [
        (GOAL_NONE, "No goal"),
        (GOAL_HOLD, "Hold steady"),
        (GOAL_TARGET, "Reach a target by a date"),
        (GOAL_FLOOR, "Never dip below a floor"),
        (GOAL_GROW, "Grow by an amount or rate"),
    ]

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
    account = models.ForeignKey(
        "accounts.Account",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="contributions",
    )
    reminder = models.ForeignKey(
        "reminders.Reminder",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="contributions",
    )
    goal_type = models.CharField(
        max_length=10, choices=GOAL_CHOICES, default=GOAL_NONE
    )
    goal_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    goal_date = models.DateField(null=True, blank=True, default=None)
    goal_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )

    def clean(self):
        # A goal is only meaningful against an account to measure.
        if self.goal_type != self.GOAL_NONE and not self.account_id:
            raise ValidationError(
                "Set an account before giving this contribution a goal."
            )
        # A target needs both a number and a deadline — solving for
        # "per paycheck" divides by the paychecks left before goal_date.
        if self.goal_type == self.GOAL_TARGET:
            if not self.goal_date:
                raise ValidationError(
                    "A target goal needs a date to reach the target by."
                )
            if self.goal_amount is None or self.goal_amount <= 0:
                raise ValidationError(
                    "A target goal needs a target balance greater than zero."
                )
        if self.goal_type == self.GOAL_FLOOR and self.goal_amount is None:
            raise ValidationError("A floor goal needs a floor balance.")
        if self.goal_type == self.GOAL_GROW:
            if not self.goal_amount and not self.goal_rate:
                raise ValidationError(
                    "A growth goal needs either an amount per month or an annual rate."
                )
        # The reminder is the apply target, so it has to be the transfer that
        # actually funds this account — otherwise applying a suggestion would
        # move money somewhere the goal does not measure.
        if self.reminder_id and self.account_id:
            if self.reminder.reminder_destination_account_id != self.account_id:
                raise ValidationError(
                    "The linked reminder must transfer into this contribution's account."
                )

    def __str__(self):
        return self.contribution


class Note(models.Model):
    """
    Model representing a note used to add notes relevant to planning.

    Fields:
    - note_text (TextField): The text of the note, unlimited length.
    - note_date (DateField): the date this note was added, defaults to today.
    """

    note_text = models.TextField()
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


class DetectedRecurring(models.Model):
    description = models.CharField(max_length=254)
    estimated_amount = models.DecimalField(max_digits=12, decimal_places=2)
    repeat = models.ForeignKey(
        Repeat, null=True, blank=True, on_delete=models.SET_NULL
    )
    next_estimated_date = models.DateField()
    transaction_ids = models.JSONField(default=list)
    is_ignored = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    suggested_tag_id = models.IntegerField(null=True, blank=True)
    suggested_account_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.description


class Budget(models.Model):
    """
    Model representing a budget.

    Fields:
    - tag_ids (CharField): A string array of tag ids.
    - name (CharFieldField): A name for this rule
    - amount (DecimalField): A max amount for this budget.
    - roll_over (BooleanField): A boolean to turn on roll over.
    - repeat (ForeignKey): A repeat object
    - start_day (DateField): A day to start this budget.
    - roll_over_amt (DecimalField): The amount rolled over.
    - active (BooleanField): A boolean to activate/deactivate budget.
    - widget (BooleanField): A boolean to show/not show in widget.
    """

    tag_ids = models.CharField(max_length=254)
    name = models.CharField(max_length=254, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    roll_over = models.BooleanField(default=True)
    repeat = models.ForeignKey(
        Repeat, null=True, on_delete=models.SET_NULL, default=None
    )
    start_day = models.DateField(default=current_date)
    roll_over_amt = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    active = models.BooleanField(default=True)
    widget = models.BooleanField(default=True)
    next_start = models.DateField(default=current_date)

    def __str__(self):
        return f"{self.name}"
