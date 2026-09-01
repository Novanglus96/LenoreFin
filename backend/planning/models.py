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


class WindfallRule(models.Model):
    """A free-text policy note for applying a windfall.

    Nothing computes on these. The caps are prose ("Until projects complete"),
    which is exactly why they are kept as written rather than turned into a
    figure: they record how the household decides to spend money that arrives
    outside the pay calendar, and a human reads them at the time.

    Fields:
    - rule (CharField): The description of the rule, limited to 254 characters.
    - cap (CharField): The cap for this rule, limited to 254 characters.
    """

    rule = models.CharField(max_length=254, unique=True)
    cap = models.CharField(max_length=254, null=True, blank=True, default=None)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.rule


class BucketMode(models.TextChoices):
    """What a bucket is *for*, stated rather than inferred.

    Every mode is the same solve with a different (floor, deadline). The base —
    the budgets this bucket funds, its dated obligations, and its buffer — is
    universal and is computed the same way for all four; the mode only decides
    how much ambition sits above that base.

    This used to be read off which nullable fields happened to be set, which
    made two genuinely different intentions indistinguishable. `target_balance`
    with no date meant "hold this from today"; with a date it meant "reach this
    by then". The same field, two demands, an order of magnitude apart in what
    they cost a paycheck.
    """

    # Fund what this bucket has to spend, and no more. The base alone.
    COVER = "cover", "Cover"
    # Hold a balance from today on. A floor under the account, every day.
    MAINTAIN = "maintain", "Maintain"
    # Reach an amount by a date. One constraint at one point, which is a far
    # weaker demand than the same figure held from today.
    GOAL = "goal", "Goal"
    # Take whatever is left once every other bucket is funded.
    MAXIMISE = "maximise", "Maximise"


class Bucket(models.Model):
    """One named pot of money and the standing intent behind it.

    A bucket is what the household actually thinks in: Grocery, Vacation,
    Ellie. It ties three things together:
    - the *intent* (`contribution_per_paycheck`, and a goal for the account),
    - the *account* the money lands in,
    - the *mechanism* (`reminder`) that actually moves it.

    A *contribution* is the money itself — what this bucket is fed each
    paycheck. The bucket is the plan for it. `contribution_per_paycheck` is
    what you intend to contribute; the linked reminder's amount is what is
    actually scheduled. The two can disagree, and the planner surfaces that
    drift rather than silently trusting either one.

    The savings plan is the whole set of buckets solved together — see
    `planning.services.savings_plan`. A bucket on its own is an intent; only
    the plan knows whether the intents fit inside a paycheck.

    Fields:
    - name (CharField): What this bucket is called — Grocery, Vacation, Ellie.
    - contribution_per_paycheck (DecimalField): The amount fed to this bucket
      each paycheck.
    - active (BooleanField): Whether this bucket is part of the plan.
    - account (ForeignKey): The account this bucket funds. Null until linked.
    - reminder (ForeignKey): The recurring transfer that moves the money. Null
      until linked.
    """

    name = models.CharField(max_length=100, unique=True)
    contribution_per_paycheck = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    # The floor the contribution to this bucket may never go below, in any
    # mode — including
    # an emergency, when discretionary funding is cut back and the difference is
    # diverted to refill the emergency fund. Null means "work it out": whatever
    # this account's budgets and dated obligations actually demand.
    minimum_per_paycheck = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, default=None
    )
    # What this bucket should still hold at its lowest point. Without it the
    # plan funds a bucket to exactly zero on its worst day, which is solvency
    # rather than comfort: one bill landing a day early overdraws it. Zero by
    # default because a derived minimum is already the smallest honest answer,
    # and a cushion is a preference the household states rather than one the
    # planner invents.
    #
    # Distinct from the funding account's buffer, which guards against posting
    # order. This one covers a bucket's own spending coming in heavier than its
    # budgets said.
    buffer = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
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
    # The budgets this bucket exists to fund. A budget is the *plan* for a
    # category's spending — user-maintained, dated, with its own repeat — which
    # makes it a far better statement of what an account must cover than a rate
    # derived from how much it happened to move last month. Left empty for a
    # bucket whose spending is genuinely sporadic; those are saved toward a
    # stated target instead of being predicted.
    budgets = models.ManyToManyField(
        "planning.Budget", blank=True, related_name="buckets"
    )
    # What this bucket is for. See `BucketMode`: it decides what ambition sits
    # above the base, and which of the fields below mean anything.
    mode = models.CharField(
        max_length=10,
        choices=BucketMode.choices,
        default=BucketMode.COVER,
    )
    # MAINTAIN only. A floor under the account, every day from now on. Funding
    # has to be enough that the worst day still clears it, which makes this the
    # most expensive thing a bucket can be asked to do — and the reason it is
    # now said explicitly rather than inferred from an undated target.
    minimum_balance = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, default=None
    )
    # GOAL only, and the two are meaningless apart. Money that has to be there
    # by a date need not be there before it, so this is one constraint at one
    # point rather than a line under the whole path.
    goal_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, default=None
    )
    goal_date = models.DateField(null=True, blank=True, default=None)
    # The spending this bucket claims responsibility for. A *claim*, not a
    # source of funding: budgets are what the plan acts on, and this is how the
    # review finds the budgets that ought to exist and do not. Gift spending is
    # the case that demands it — 2,023 a year across 44 expenses that no budget
    # described, invisible until a bucket said "that spending is mine".
    #
    # Deriving this from the linked budgets' own tags cannot work: you would
    # need the budget to exist in order to notice the budget is missing. Left
    # unscoped, the report is led by transfers, income and card payments, which
    # dwarf every real category.
    scope_tags = models.ManyToManyField(
        "tags.Tag", blank=True, related_name="buckets"
    )
    # The whole families of spending this bucket owns. Naming a main tag claims
    # every tag under it, including ones that do not exist yet — which is the
    # difference between a rule and a snapshot. Listing children individually
    # was how Ellie came to claim eight Kids tags: add "Kids / Sports" tomorrow
    # and the spending lands in a category no bucket owns, with nothing to say
    # so. A bucket is almost always named after a family anyway (Reno, Pet,
    # Vacation), so this is also the shorter thing to say.
    scope_main_tags = models.ManyToManyField(
        "tags.MainTag", blank=True, related_name="buckets"
    )
    # Where the credit-card rewards land when they are cashed in. They accrue
    # all year and are redeemed in one lump in November, which for this
    # household is the largest single inflow the gift budget sees — and one the
    # planner cannot otherwise know about, because nobody enters next
    # November's statement credit a year ahead.
    receives_rewards = models.BooleanField(default=False)
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

    def claimed_tags(self):
        """Every tag this bucket owns, however it was claimed.

        The union of the tags named one by one and every tag under a claimed
        main tag. One place, because three callers have to agree about it: the
        plan measures these, the review reports on them, and the form shows
        them.
        """
        from django.db.models import Q

        from tags.models import Tag

        if not self.pk:
            return Tag.objects.none()
        return (
            Tag.objects.filter(
                Q(pk__in=self.scope_tags.values("pk"))
                | Q(parent_id__in=self.scope_main_tags.values("pk"))
            )
            .distinct()
        )

    @property
    def sweep(self) -> bool:
        """Whether this bucket absorbs the remainder.

        Derived, not stored. A bucket that takes what is left is one *mode* of
        being a bucket, and having both a mode and a boolean saying the same
        thing is how the two drift apart.
        """
        return self.mode == BucketMode.MAXIMISE

    def clean(self):
        # Each mode is defined by exactly one set of fields, and a field that
        # means nothing in the chosen mode is a statement nobody will ever see
        # honoured. Rejecting it here is kinder than storing it and ignoring
        # it, which is what the old inferred scheme did.
        if self.mode == BucketMode.MAINTAIN:
            if self.minimum_balance is None:
                raise ValidationError(
                    "A bucket set to Maintain needs the balance to hold."
                )
            if self.minimum_balance < 0:
                raise ValidationError("A minimum balance cannot be negative.")
        elif self.minimum_balance is not None:
            raise ValidationError(
                "A minimum balance only applies to a bucket set to Maintain."
            )

        if self.mode == BucketMode.GOAL:
            # Neither half is any use alone: an amount with no date is a
            # Maintain wearing a goal's clothes, which is the exact confusion
            # this mode exists to end.
            if self.goal_amount is None or self.goal_date is None:
                raise ValidationError(
                    "A goal needs both an amount and the date to reach it by."
                )
            if self.goal_amount < 0:
                raise ValidationError("A goal amount cannot be negative.")
        elif self.goal_amount is not None or self.goal_date is not None:
            raise ValidationError(
                "A goal amount and date only apply to a bucket set to Goal."
            )

        # A balance target is a statement about an account, so it needs an
        # account to be a statement about.
        if (
            self.mode in (BucketMode.MAINTAIN, BucketMode.GOAL)
            and not self.account_id
        ):
            raise ValidationError(
                "Set an account before giving this bucket a balance to reach."
            )
        if self.minimum_per_paycheck is not None and self.minimum_per_paycheck < 0:
            raise ValidationError("A minimum cannot be negative.")
        if self.buffer is not None and self.buffer < 0:
            raise ValidationError("A buffer cannot be negative.")
        # The reminder this bucket points at is the one the plan *adjusts*, so
        # it has to be one that actually funds the account. Pointing at a
        # transfer that lands somewhere else would have the plan raising a
        # figure that never reaches this bucket, and the funding it does
        # receive would be reported as money nobody set.
        if self.reminder_id and self.account_id:
            destination = getattr(
                self.reminder, "reminder_destination_account_id", None
            )
            if destination and destination != self.account_id:
                raise ValidationError(
                    "That reminder does not pay into this bucket's account, so "
                    "the plan cannot use it to fund this bucket."
                )

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
