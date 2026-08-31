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

    contribution = models.CharField(max_length=20, unique=True)
    per_paycheck = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    # The floor this contribution may never go below, in any mode — including
    # an emergency, when discretionary funding is cut back and the difference is
    # diverted to refill the emergency fund. Null means "work it out": whatever
    # this account's budgets and dated obligations actually demand.
    minimum_per_paycheck = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, default=None
    )
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
    # The budgets this bucket exists to fund. A budget is the *plan* for a
    # category's spending — user-maintained, dated, with its own repeat — which
    # makes it a far better statement of what an account must cover than a rate
    # derived from how much it happened to move last month. Left empty for a
    # bucket whose spending is genuinely sporadic; those are saved toward a
    # stated target instead of being predicted.
    budgets = models.ManyToManyField(
        "planning.Budget", blank=True, related_name="contributions"
    )
    # What this account should accumulate to. Funding stops once the balance is
    # there, which is what frees capacity for everything below it in priority.
    target_balance = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, default=None
    )
    # When the target must be met. Null means "hold it from now on" rather than
    # "reach it by a date", which are different problems.
    target_date = models.DateField(null=True, blank=True, default=None)
    # The spending tags this bucket exists to cover, for the spending no budget
    # describes. Birthdays are the case that demands it: they are real, they
    # recur, they are spread unevenly through the year, and writing a budget per
    # person is a chore nobody will keep up. What was actually spent on these
    # tags over the last year is better evidence than a budget that does not
    # exist. Tags a linked budget already covers are ignored here — counting the
    # Christmas budget and Christmas spending both would fund Christmas twice.
    tags = models.ManyToManyField(
        "tags.Tag", blank=True, related_name="contributions"
    )
    # Where the credit-card rewards land when they are cashed in. They accrue
    # all year and are redeemed in one lump in November, which for this
    # household is the largest single inflow the gift budget sees — and one the
    # planner cannot otherwise know about, because nobody enters next
    # November's statement credit a year ahead.
    receives_rewards = models.BooleanField(default=False)
    # Takes whatever is left once everything else is funded. More than one is
    # allowed; `sweep_share` decides how they divide it.
    sweep = models.BooleanField(default=False)
    # Relative weight when several accounts sweep. Two sweeps at 3 and 1 split
    # the remainder three to one. Equal by default, which is what it did before
    # there was a way to say otherwise.
    sweep_share = models.PositiveIntegerField(default=1)
    # Lower is funded first. When capacity runs out the planner stops filling
    # targets in this order, so the ranking is what decides who goes short —
    # sharing a shortage equally across every bucket is not a decision anyone
    # would actually make. It is also the order a windfall is applied in.
    priority = models.IntegerField(default=100)
    # Whether this account may be borrowed from to cover a gap somewhere else.
    # The planner schedules bridging transfers — money moved across for a few
    # days and paid back when the funding account recovers — and it ranks
    # sources by what they earn and how important they are. Neither of those
    # captures "this is my daughter's savings account and it is not a slush
    # fund", so that is stated rather than inferred. On by default: most
    # buckets are the household's own money in a different pocket.
    lendable = models.BooleanField(default=True)

    def clean(self):
        # A target is a statement about an account's balance, so it needs an
        # account to be a statement about.
        if self.target_balance is not None and not self.account_id:
            raise ValidationError(
                "Set an account before giving this contribution a target."
            )
        if self.target_balance is not None and self.target_balance < 0:
            raise ValidationError("A target balance cannot be negative.")
        if self.target_date and self.target_balance is None:
            raise ValidationError(
                "A target date needs a target balance to reach by then."
            )
        if self.minimum_per_paycheck is not None and self.minimum_per_paycheck < 0:
            raise ValidationError("A minimum cannot be negative.")
        # A sweep takes what is left over, so a ceiling on it is a contradiction
        # — the leftover is defined by everything else, not by this row.
        if self.sweep and self.target_balance is not None:
            raise ValidationError(
                "A sweep contribution takes whatever is left, so it cannot also "
                "have a target balance."
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
    # For a leaf budget, what it plans to spend. For a budget with children the
    # stored value is ignored — see `planned_amount`, which adds the children
    # up. A parent exists to total its parts, not to hold a figure of its own
    # that can drift away from them: Christmas was budgeted at 1,995 while the
    # twenty-three people under it summed to 1,130, and nothing anywhere
    # reconciled the two.
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    # One level only, the same rule accounts follow. A budget either totals
    # others or is one of them.
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="children",
    )
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

    @property
    def is_parent(self):
        return self.pk is not None and self.children.filter(active=True).exists()

    @property
    def planned_amount(self):
        """What this budget plans to spend, in its own cadence.

        Derived for a parent, stored for everything else. Children are
        converted into the parent's cadence first — a yearly parent over
        monthly children is a legitimate thing to want, and summing the raw
        figures would be out by a factor of twelve.
        """
        from planning.services.budget_math import parent_planned_amount

        if not self.is_parent:
            return self.amount
        return parent_planned_amount(self)

    def clean(self):
        # One level, so a parent's total is always the sum of leaves and never
        # of other totals.
        if self.parent_id:
            if self.pk and self.parent_id == self.pk:
                raise ValidationError("A budget cannot be its own parent.")
            parent = Budget.objects.filter(pk=self.parent_id).first()
            if parent and parent.parent_id:
                raise ValidationError(
                    "That budget is already part of another total. Budgets "
                    "only nest one level deep."
                )
            if self.pk and self.children.exists():
                raise ValidationError(
                    "This budget totals others, so it cannot itself be part of "
                    "a total."
                )

    def __str__(self):
        return f"{self.name}"
