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


class WindfallRule(models.Model):
    """Where money arriving outside the pay calendar goes, in order.

    A rule that names a bucket is computed on: the plan proposes its order and
    how much it takes (the bucket's shortfall against its goal), and the owner
    may override either. A rule with no bucket is a note the owner reads
    ("repay the money market first") and nothing computes on.

    Fields:
    - rule (CharField): Description of the rule.
    - bucket (ForeignKey): The bucket this rule tops up, if it names one.
    - cap (CharField): The cap as prose, for rules whose limit is not a figure.
    - cap_amount (Decimal): The most this rule takes from one windfall. Null
      means "whatever the bucket's goal still needs".
    - order (int): Position in the waterfall, lowest first.
    """

    rule = models.CharField(max_length=254, unique=True)
    bucket = models.ForeignKey(
        "planning.Bucket",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="windfall_rules",
    )
    cap = models.CharField(max_length=254, null=True, blank=True, default=None)
    cap_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, default=None
    )
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.rule


class Bucket(models.Model):
    """One named pot of money, the account it lives in, and what feeds it.

    - `contribution_per_paycheck` is what the household intends to put in.
    - `reminder` is the recurring transfer that actually moves it.
    - `goal_amount` is soft: falling short is flagged for windfalls, never a
      failure. Once the account reaches it, the plan stops funding the bucket
      and frees that money for buckets still short of theirs.
    - `goal_date` is when the goal is judged; null means the end of the plan.

    Fields:
    - name (CharField): Grocery, Vacation, Ellie.
    - contribution_per_paycheck (Decimal): Planned amount each paycheck.
    - goal_amount (Decimal): Balance to reach, optional.
    - goal_date (Date): When to have reached it, optional.
    - active (bool): Whether this bucket is part of the plan.
    - account (ForeignKey): Where the money lands.
    - reminder (ForeignKey): The transfer that moves it.
    """

    name = models.CharField(max_length=100, unique=True)
    contribution_per_paycheck = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    goal_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, default=None
    )
    goal_date = models.DateField(null=True, blank=True, default=None)
    active = models.BooleanField(default=True)
    account = models.ForeignKey(
        "accounts.Account",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="buckets",
    )
    reminder = models.ForeignKey(
        "reminders.Reminder",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="buckets",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


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


class PlanAcceptance(models.Model):
    """A savings plan the household committed to, and the window it covers.

    The plan itself is computed on every request; this records what was agreed
    so the page can say when, and so the whole act can be undone.
    """

    accepted_on = models.DateField()
    window_start = models.DateField()
    window_end = models.DateField()
    total_per_paycheck = models.DecimalField(max_digits=12, decimal_places=2)
    # Ideal, workable or insolvent at the moment of accepting. An insolvent
    # plan can be accepted, but only deliberately, and the record says so.
    verdict = models.CharField(max_length=10, default="ideal")
    reverted_on = models.DateField(null=True, blank=True, default=None)
    # Restored from a backup: the reminders it wrote are linked again, but the
    # snapshots of what it displaced name ids from another database, so it
    # cannot be undone.
    imported = models.BooleanField(default=False)
    # The bucket-linked windfall rules as they stood, since accepting a plan
    # replaces them with the plan's overage order.
    rules_snapshot = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-accepted_on", "-id"]

    def __str__(self):
        return f"Plan {self.window_start}..{self.window_end} accepted {self.accepted_on}"


class AcceptedBucket(models.Model):
    """One bucket's part of an accepted plan, and everything it displaced.

    Accepting can do three things to a bucket: change its amount from the
    first paycheck of the window, create it, or retire it. Each writes or
    trims reminders; the `previous_*` fields and `created_reminders` are what
    let revert put things back exactly as they were.
    """

    ACTION_CHANGE = "change"
    ACTION_CREATE = "create"
    ACTION_REMOVE = "remove"
    ACTIONS = [
        (ACTION_CHANGE, "Change"),
        (ACTION_CREATE, "Create"),
        (ACTION_REMOVE, "Remove"),
    ]

    acceptance = models.ForeignKey(
        PlanAcceptance, on_delete=models.CASCADE, related_name="buckets"
    )
    bucket = models.ForeignKey(
        "planning.Bucket",
        null=True,
        on_delete=models.SET_NULL,
        related_name="accepted",
    )
    bucket_name = models.CharField(max_length=100)
    action = models.CharField(max_length=10, choices=ACTIONS, default=ACTION_CHANGE)
    per_paycheck = models.DecimalField(max_digits=12, decimal_places=2)
    previous_per_paycheck = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    previous_goal_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, default=None
    )
    previous_goal_date = models.DateField(null=True, blank=True, default=None)
    previous_active = models.BooleanField(default=True)
    # Every funding reminder this acceptance trimmed or deleted, as it stood
    # before: a list of field dicts including its id. Revert restores the
    # fields, or recreates the reminder if it was deleted.
    reminder_snapshots = models.JSONField(default=list, blank=True)
    # Which reminder the bucket pointed at before, so revert can point it back
    # (at the recreated copy, if accepting deleted it).
    previous_reminder_id = models.IntegerField(null=True, blank=True, default=None)
    # Reminders this acceptance wrote, deleted again on revert.
    created_reminders = models.ManyToManyField(
        "reminders.Reminder", blank=True, related_name="+"
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.bucket_name}: {self.action} {self.per_paycheck}"


class WindfallApplication(models.Model):
    """A lump sum the household spent, and where it went.

    `applied_on` is when it was decided; `arrival_date` is what the transfers
    are dated, because a bonus is often planned days before it lands.
    """

    applied_on = models.DateField()
    arrival_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    allocated = models.DecimalField(max_digits=12, decimal_places=2)
    source_account = models.ForeignKey(
        "accounts.Account",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="windfalls",
    )
    reverted_on = models.DateField(null=True, blank=True, default=None)

    class Meta:
        ordering = ["-arrival_date", "-id"]

    def __str__(self):
        return f"Windfall of {self.amount} on {self.arrival_date}"


class WindfallAllocation(models.Model):
    """One bucket's share of a windfall, and the transfer that delivered it."""

    application = models.ForeignKey(
        WindfallApplication, on_delete=models.CASCADE, related_name="allocations"
    )
    bucket = models.ForeignKey(
        "planning.Bucket",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="windfall_allocations",
    )
    bucket_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    suggested = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transaction = models.ForeignKey(
        "transactions.Transaction",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="windfall_allocations",
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.bucket_name}: {self.amount}"
