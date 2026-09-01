"""A savings plan that is proven before it is offered.

The planner this replaces asked each bucket "what would make you healthy?" and
added the answers up. That is the wrong question twice over: the answers are not
constrained by what there is to allocate, and nothing ever checked that the
resulting plan actually works.

This one runs the other way round.

1. `pay_calendar` — when the paychecks land over the horizon, from the paycheck
   reminders. Everything downstream is expressed per paycheck, so the calendar
   is what makes "per paycheck" mean a date rather than an average.

2. `baseline_path` — each account's projected balance with its own contribution
   *removed*, so the plan is superimposed on an account that is not already
   being funded. Ad-hoc spending no reminder describes is drip-fed onto the path
   here, because a bucket whose entire purpose is unscheduled spending would
   otherwise look like it needed nothing at all.

3. `required_rate` — the smallest per-paycheck contribution that keeps a path
   above its floor. Closed-form: a contribution is a fixed transfer on known
   dates, so the balance under it is `baseline(t) + rate * paychecks_so_far(t)`,
   and the binding constraint is whichever date needs the most.

4. `capacity` — the same arithmetic applied to the funding account, in two
   figures. What the year affords is the constraint on the plan; what the path
   affords unaided is advisory, and the difference between them is money that
   has to be moved across rather than money that cannot be saved.

5. `build_savings_plan` — fund every minimum, then fill goals in priority
   order until the money runs out, then sweep the remainder. The result is the
   savings plan: every bucket solved together, because a bucket on its own
   cannot know whether it fits inside a paycheck.

6. `_verify` — re-check the finished plan against every path, and classify what
   it finds. A dip the account climbs out of is a timing problem with a
   one-off fix; a dip it never recovers from is the plan being wrong. Only the
   second invalidates a plan.

The whole thing costs one forecast pass per account. Candidate allocations are
evaluated by superposition rather than by re-running the forecast, which is
exact for a fixed transfer and turns a ~1.6s simulation into arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal

from django.db.models import Q

from accounts.models import Account
from planning.models import Bucket
from planning.services.budget_math import (
    amount_per_year,
    budget_events,
    spending_budgets,
)
from planning.services.budget_review import BudgetSuggestion, review_budgets
from planning.services.income_review import IncomeDrift, review_income
from planning.services.rewards import reward_outlook
from planning.services.planner import (
    DAYS_PER_MONTH,
    DAYS_PER_YEAR,
    analyze_account_trend,
    funding_account_id,
    occurrences_per_year,
    paychecks_per_year,
)
from reminders.models import Reminder
from transactions.services import get_account_transactions_and_balances

# What the funding account must still hold at its lowest point. Small by
# default and deliberately so: this household keeps a month's pay in a separate
# emergency account, so a large checking cushion would only be idle money. It is
# a parameter because that is not true of everyone.
DEFAULT_BUFFER = Decimal("10.00")

# Sanity bound on a derived minimum. Without it a bucket that dips the day
# before its first paycheck asks for the entire shortfall in one go.
MIN_PAYCHECKS_TO_SOLVE = Decimal("2")

# How long an account may sit below its floor and still count as a timing
# problem rather than a broken plan. Measured in paydays, not days, because the
# question is "has money arrived and the account is *still* under water?" — that
# scales with how the household is actually paid instead of assuming a
# fortnight. Two paydays in and not recovered is not a dip, it is a deficit.
MAX_TIMING_DIP_PAYDAYS = 2

# How often it is reasonable to have to move money across to cover a gap.
# Owner's call, 2026-08-31, made against the real trade-off: this household can
# allocate 2,557 a paycheck with no bridging at all, 2,773 with three transfers
# a year, or the whole 2,893 the year affords — at which point checking dips
# every single pay cycle and the "plan" is really a fortnightly shuffle. Three
# sits just before that knee. It caps *discretionary* filling only; a minimum
# the household has stated is funded whatever bridging it implies.
MAX_BRIDGES_PER_YEAR = 3

# A contribution is set up as a standing transfer at a bank, by a person, so
# the figures have to be ones a person would actually type. Owner's call,
# 2026-08-31: five dollars.
#
# Which way each figure rounds is not a style question — it is what keeps the
# guarantees true. A minimum rounded down is short by construction, so minimums
# round UP. Discretionary filling rounds DOWN, because rounding every line up
# put this household's plan at 2,895 against the 2,893.11 the year affords: a
# plan that no longer fits, produced by tidying it. A bridging transfer rounds
# UP, because covering all but four dollars of a gap does not cover the gap.
ROUNDING_INCREMENT = Decimal("5")


def round_up_to(value: Decimal, step: Decimal = ROUNDING_INCREMENT) -> Decimal:
    """The next multiple of `step` at or above `value`."""
    if step <= 0:
        return value
    stepped = (value / step).quantize(Decimal("1"), rounding=ROUND_CEILING) * step
    return stepped.quantize(Decimal("0.01"))


def round_down_to(value: Decimal, step: Decimal = ROUNDING_INCREMENT) -> Decimal:
    """The previous multiple of `step` at or below `value`."""
    if step <= 0:
        return value
    if value <= 0:
        return Decimal("0.00")
    stepped = (value / step).quantize(Decimal("1"), rounding=ROUND_FLOOR) * step
    return stepped.quantize(Decimal("0.01"))


@dataclass
class PathPoint:
    day: int
    when: date
    balance: Decimal


@dataclass
class BucketPlan:
    """One bucket's share of the plan, and the evidence behind it."""

    bucket_id: int
    bucket_name: str
    account_id: int | None
    account_name: str | None
    priority: int
    sweep: bool
    # Relative weight when several accounts sweep the remainder.
    sweep_share: int
    # Whether this account may be borrowed from to bridge someone else's gap.
    lendable: bool
    # Whether the card rewards are cashed into this account.
    receives_rewards: bool
    paychecks_per_year: Decimal

    current_per_paycheck: Decimal
    minimum_per_paycheck: Decimal
    minimum_is_stated: bool
    target_per_paycheck: Decimal
    planned_per_paycheck: Decimal

    # What this bucket's linked budgets come to, and which they are. This is the
    # planned spending it exists to cover.
    budgeted_per_paycheck: Decimal
    budget_names: list[str]
    target_balance: Decimal | None
    projected_low: Decimal
    projected_low_date: date | None
    # What the account has actually been spending, measured. Never an input to
    # the plan — budgets are — but a budget that disagrees with reality by a
    # wide margin is worth saying out loud.
    observed_spend_per_month: Decimal
    spend_variance_per_paycheck: Decimal
    reason: str
    warning: str | None = None
    # Both are worked out once the allocation is settled, so they are filled in
    # afterwards rather than passed in.
    #
    # What cutting this line back to the plan would free, against what is being
    # contributed today. Positive means the account is getting more than it
    # needs.
    # What the linked tags actually cost over the last year, and which they
    # are. Spending no budget describes, funded from evidence instead.
    measured_per_year: Decimal = Decimal("0.00")
    measured_tag_names: list[str] = field(default_factory=list)
    # What the account's own budgets and dated bills actually demand, before
    # any stated floor is applied. Reported separately because a stated minimum
    # *hides* this figure: the plan echoes the number you typed and there is no
    # way to tell "we budgeted this perfectly" from "nobody looked".
    derived_minimum_per_paycheck: Decimal = Decimal("0.00")
    # Card rewards expected to land in this account, and when.
    rewards_expected: Decimal = Decimal("0.00")
    rewards_on: date | None = None
    # Funding this bucket receives that the plan does not decide — a
    # dependent-care transfer, say. Already on the path, so the solved rates
    # allow for it; named here because a line reporting 85.00 into an account
    # that actually receives 362.77 cannot be reasoned about.
    other_funding_per_paycheck: Decimal = Decimal("0.00")
    other_funding_names: list[str] = field(default_factory=list)
    # How much spending this bucket has claimed, and what of it nothing funds.
    # Silence used to mean two different things — correctly configured, and
    # never set up — and eight of ten buckets were the second.
    claimed_tag_count: int = 0
    unbudgeted_per_year: Decimal = Decimal("0.00")
    coverage: str | None = None
    freed_per_paycheck: Decimal = Decimal("0.00")
    # The part of this line nothing asked for: allocated beyond every stated
    # minimum and target because it had nowhere else to go.
    optional_per_paycheck: Decimal = Decimal("0.00")


@dataclass
class SavingsPlan:
    generated_for: date
    horizon_months: int
    buffer: Decimal
    paychecks: list[date]
    paychecks_in_horizon: int

    # Three figures, each answering a different question.
    # What the plan allocates up to: the most that can be put away while the
    # bridging stays within budget.
    capacity_per_paycheck: Decimal
    # The largest plan that never needs money moved across at all. Advisory —
    # a plan above it is still valid, it just carries a bridging schedule.
    path_capacity_per_paycheck: Decimal
    # The year's surplus over its paydays. The hard ceiling: a plan above this
    # is not badly timed, it is unaffordable.
    horizon_capacity_per_paycheck: Decimal
    # Set when the plan is affordable but arrives late: the date the funding
    # account runs short, and the one-off transfer that covers it.
    timing_shortfall: dict | None
    minimums_total: Decimal
    targets_total: Decimal
    planned_total: Decimal
    current_total: Decimal
    unallocated: Decimal
    # What the plan frees compared with what is being contributed today. The
    # planner is not only for finding money to save — an account that has
    # already got what it needs is money doing nothing, and saying so is half
    # the value of proving the plan.
    freed_per_paycheck: Decimal
    # Allocated beyond every stated minimum and target, because a sweep account
    # exists to absorb it. Not a goal being met — a goal nobody has written
    # down, or money that could simply be spent.
    optional_per_paycheck: Decimal

    feasible: bool
    verified: bool

    # Funding the plan does not decide, across every bucket. `planned_total` is
    # what the plan moves; this is what arrives anyway, and the two together are
    # what the household actually puts away. Unchanged by the plan, so it drops
    # out of any before-and-after comparison — which is exactly why quoting the
    # allocation on its own reads as a smaller savings rate than the truth.
    other_funding_total: Decimal = Decimal("0.00")
    lines: list[BucketPlan] = field(default_factory=list)
    breaches: list[dict] = field(default_factory=list)
    # Where the money for each timing dip comes from, and when it goes back.
    # A plan is the allocation and this schedule together, not one without
    # the other.
    bridges: list[dict] = field(default_factory=list)
    # Where the budgets disagree with the last twelve months. Budgets are the
    # only thing the plan acts on, so this is how measurement gets a say:
    # accepting one changes a budget, and that changes the plan.
    budget_suggestions: list[BudgetSuggestion] = field(default_factory=list)
    # Where the income reminders disagree with what actually arrived. Capacity
    # is built from those reminders, so a stale one makes every figure here
    # wrong in the same direction — and silently, because the plan simply
    # reports a smaller household than the one that exists.
    income_drift: list[IncomeDrift] = field(default_factory=list)
    levers: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _field(row, name):
    return row[name] if isinstance(row, dict) else getattr(row, name, None)


def pay_calendar(
    today: date, end_date: date, account_id: int | None = None
) -> list[date]:
    """The dates money actually arrives, from the paycheck reminders.

    Grouped by date rather than listed per reminder: a household can have
    several earners paid on the same day, and two cheques on one date is still
    one payday. Everything the planner produces is "per paycheck", so this is
    what gives that unit a meaning more precise than 26-ish a year.
    """
    account_id = account_id or funding_account_id()
    if account_id is None:
        return []

    dates: set[date] = set()
    for reminder in Reminder.objects.filter(
        Q(reminder_source_account_id=account_id)
        | Q(reminder_destination_account_id=account_id),
        transaction_type__slug="income",
    ).select_related("repeat", "transaction_type"):
        if reminder.end_date and reminder.end_date < today:
            continue
        repeat = reminder.repeat
        if repeat is None:
            continue
        period = (
            Decimal(repeat.days or 0)
            + Decimal(repeat.weeks or 0) * 7
            + Decimal(repeat.months or 0) * DAYS_PER_MONTH
            + Decimal(repeat.years or 0) * DAYS_PER_YEAR
        )
        if period <= 0:
            continue
        cursor = reminder.next_date or reminder.start_date or today
        last = end_date
        if reminder.end_date and reminder.end_date < last:
            last = reminder.end_date
        step = int(period)
        guard = 0
        while cursor <= last and guard < 400:
            if cursor >= today:
                dates.add(cursor)
            cursor = cursor + timedelta(days=step)
            guard += 1

    return sorted(dates)


def _paychecks_by_day(paychecks: list[date], today: date) -> list[int]:
    """Days-from-today for each payday, so a path point can count them cheaply."""
    return [(d - today).days for d in paychecks]


def _paychecks_before(day: int, paycheck_days: list[int]) -> int:
    """How many paydays have landed by `day`.

    A contribution paid *on* the day money is needed still counts — the transfer
    and the withdrawal both happen that day, and ordering within a day is not
    something the forecast models.
    """
    count = 0
    for pd in paycheck_days:
        if pd <= day:
            count += 1
        else:
            break
    return count


def tag_spend_events(
    bucket: Bucket, today: date, end_date: date
) -> tuple[list[tuple[date, Decimal]], Decimal, list[str]]:
    """What this bucket's tags actually cost last year, replayed a year on.

    Budgets are the better input wherever one exists — they are the user's own
    statement of intent, and measurement is only its shadow. But some spending
    is real, recurring and never going to be written down: birthdays are the
    case that forced this. There are a dozen of them, they land unevenly across
    the year, and nobody is going to maintain a budget per person. What was
    actually spent is the only evidence there is.

    Replayed as **dated events**, not as a rate, for the same reason budgets
    are: when the money is needed decides how much must be saved by then. And
    dates are what the history is good for — a birthday in March recurs in
    March, so last year's dates shifted forward a year are a far better guess
    than a twelfth of the total every month.

    Tags that a linked budget already covers are excluded. Counting the
    Christmas budget *and* Christmas spending would fund Christmas twice, which
    is the same double-count that made this household's grocery minimum come
    out at 696 from a 460 budget.
    """
    import json

    from transactions.models import TransactionDetail

    linked = list(bucket.claimed_tags().select_related('parent', 'child'))
    if not linked:
        return [], Decimal("0.00"), []

    covered: set[int] = set()
    for budget in bucket.budgets.all():
        if budget.tag_ids:
            try:
                covered.update(json.loads(budget.tag_ids))
            except (ValueError, TypeError):
                continue

    measured = [tag for tag in linked if tag.pk not in covered]
    if not measured:
        return [], Decimal("0.00"), []

    window_start = today - timedelta(days=int(DAYS_PER_YEAR))
    details = (
        TransactionDetail.objects.filter(
            tag_id__in=[tag.pk for tag in measured],
            transaction__transaction_date__gte=window_start,
            transaction__transaction_date__lt=today,
        )
        .exclude(transaction__status__slug="archived")
        .select_related("transaction")
    )

    # One event per date rather than per line: three presents bought on the
    # same afternoon are one demand on the account.
    by_day: dict[date, Decimal] = {}
    total = Decimal("0")
    for detail in details:
        # Summed rather than taken as absolute values, so a refund nets off the
        # spending it reverses instead of counting as more money to find.
        amount = detail.detail_amt or Decimal("0")
        when = detail.transaction.transaction_date + timedelta(
            days=int(DAYS_PER_YEAR)
        )
        if when < today or when > end_date:
            continue
        by_day[when] = by_day.get(when, Decimal("0")) + amount
        total += amount

    names = [
        f"{tag.parent.tag_name if tag.parent else '?'}"
        + (f"/{tag.child.tag_name}" if tag.child else "")
        for tag in measured
    ]
    events = sorted(by_day.items())
    return events, abs(total).quantize(Decimal("0.01")), names


def budget_per_paycheck(budget) -> Decimal:
    """A budget's planned spend in the cadence the planner allocates in.

    Uses `planned_amount`, so a parent reports the sum of its children rather
    than a stored figure that has drifted away from them.
    """
    return (
        amount_per_year(budget.planned_amount, budget.repeat)
        / Decimal("26.0893")
    ).quantize(Decimal("0.01"))


def baseline_path(
    account_id: int,
    today: date,
    end_date: date,
    exclude_reminder_ids: set[int],
    spend_events: list[tuple[date, Decimal]] | None = None,
    replace_adhoc_reimbursements_to: int | None = None,
) -> tuple[list[PathPoint], Decimal]:
    """An account's projected balance with named flows removed and budgets added.

    `exclude_reminder_ids` takes out the transfers the plan is deciding, so the
    plan is superimposed on an account nobody is funding yet. Their deltas are
    backed out of the running balance rather than merely skipped, otherwise
    every later point still carries them.

    Identified by the reminder they came from, not by what that reminder is
    called. A description is a label a user may edit at any time, and applying
    a plan is *expected* to rename these transfers to a convention — at which
    point matching on the name would silently stop excluding them, count the
    funding twice, and drop every requirement the planner reports. The id
    survives a rename; the name does not. (History is matched by description
    still, in `analyze_account_trend`, because a recorded `Transaction` carries
    no link back to the reminder that produced it — only the forecast rows do.)

    `spend_events` are the budgets this bucket funds. The forecast is a
    known-commitments engine — it projects reminders, recorded transactions and
    the card bills those produce — so discretionary spending that has not been
    entered yet is simply absent from the future. For the funding account that
    is harmless, because the missing card payment and the missing reimbursement
    cancel out. For a bucket it is not: that spending is the whole reason the
    bucket exists. The budget is the user's own statement of it, which beats a
    rate derived from how much the account happened to move last month.
    """
    try:
        # `totals_only=True` skips the tag lookups and display annotations that
        # dress a transaction up for the ledger screen. The planner reads only
        # the date, the balance, the description and the account ids, all of
        # which come back either way — identical rows, five times faster, and
        # this runs once per account.
        rows, opening = get_account_transactions_and_balances(
            end_date, account_id, True, True, today, False
        )
    except Exception:
        return [], Decimal("0")

    opening = Decimal(str(opening))
    running = opening
    previous = opening
    # Everything that moves the balance, forecast and budget alike, merged into
    # one ordered walk.
    steps: list[tuple[int, date, Decimal]] = []

    for row in rows:
        raw = _field(row, "balance")
        if raw is None:
            continue
        balance = Decimal(str(raw))
        delta = balance - previous
        previous = balance
        when = _field(row, "transaction_date")
        if when is None:
            continue
        # Excluded flows contribute no delta, but the date is still a point on
        # the path. Skipping them outright made the path collapse to one entry
        # for any bucket whose only modelled flow is the contribution being
        # planned, and a one-point path can never show drift accumulating.
        keep = _field(row, "reminder_id") not in exclude_reminder_ids
        if keep and replace_adhoc_reimbursements_to is not None:
            reimburses = (
                _field(row, "destination_account_id")
                == replace_adhoc_reimbursements_to
                and _field(row, "source_account_id") == account_id
                and _field(row, "reminder_id") is None
            )
            if reimburses:
                keep = False
        steps.append(
            ((when - today).days, when, delta if keep else Decimal("0"))
        )

    for when, amount in spend_events or []:
        steps.append(((when - today).days, when, amount))

    steps.sort(key=lambda step: step[0])

    # One point per day, holding that day's closing balance. Several
    # transactions can land on one date and the forecast does not model their
    # order, so a running balance that dips mid-day and recovers before the day
    # is out says nothing except that the rows were sorted arbitrarily. Reading
    # closing balances also makes the path agree with `_paychecks_before`, which
    # already counts a payday landing *on* the day it is needed. Judging every
    # intermediate row instead invented a 994.16 shortfall on one October
    # afternoon and six more like it, none of which exist at close of business.
    #
    # A household that wants protection from posting order sets a larger buffer;
    # that is the honest dial for it, and it is per household.
    by_day: dict[int, PathPoint] = {}
    for day, when, delta in steps:
        running += delta
        by_day[day] = PathPoint(
            day=day, when=when, balance=running.quantize(Decimal("0.01"))
        )
    path: list[PathPoint] = [by_day[day] for day in sorted(by_day)]
    # Today is a point on every path, even for an account with nothing
    # scheduled for weeks. Starting at the first modelled transaction leaves the
    # days before it unexamined, which reads as "this account holds nothing"
    # rather than "nothing happens here yet".
    if not path or path[0].day > 0:
        path.insert(
            0,
            PathPoint(day=0, when=today, balance=opening.quantize(Decimal("0.01"))),
        )

    # The horizon's end is a point in its own right. Without it an account whose
    # last modelled transaction is in month three looks safe for the rest of the
    # year, however fast it is drifting.
    horizon_days = (end_date - today).days
    if not path or path[-1].day < horizon_days:
        path.append(
            PathPoint(
                day=horizon_days,
                when=end_date,
                balance=running.quantize(Decimal("0.01")),
            )
        )
    return path, opening


@dataclass
class Dip:
    """One contiguous run below an account's floor.

    The owner's rule for what counts as "no account goes negative" is not
    "balance >= 0 at every point". It is:

        Small dips or short periods that can be covered by moving money are
        acceptable. Those are just timing issues if at the end of the plan the
        account is rectified.

    So a dip has to be measured, not merely detected: how deep, how long, and
    whether the account climbs back out. `depth` is exactly the one-off transfer
    that erases it, which is also the input the bridging schedule is built from.
    """

    start: date
    start_day: int
    low: Decimal
    low_when: date
    depth: Decimal
    recovers_on: date | None
    days_below: int
    paydays_below: int

    @property
    def kind(self) -> str:
        """`one_off` — a bridge fixes it. `structural` — the plan is wrong.

        A dip the account never climbs out of is the plan failing: the money was
        never there, and no transfer covers a permanent deficit. A dip that is
        still open after two paydays have landed is the same thing arriving
        slowly. Everything else is timing, and timing is a transfer.

        Depth deliberately does not appear here. However deep a dip is, if the
        account recovers, the plan itself is sound and what is needed is a
        movement of money — whether one can actually be found is the bridging
        solver's question, and it escalates the dip if the answer is no.
        """
        if self.recovers_on is None:
            return "structural"
        if self.paydays_below > MAX_TIMING_DIP_PAYDAYS:
            return "structural"
        return "one_off"

    @property
    def why(self) -> str:
        if self.recovers_on is None:
            return (
                f"Below the floor from {self.start} to the end of the plan, "
                f"{self.depth} under at worst. The account never recovers, so "
                f"no transfer fixes this."
            )
        if self.paydays_below > MAX_TIMING_DIP_PAYDAYS:
            return (
                f"Below the floor from {self.start} until {self.recovers_on} — "
                f"{self.paydays_below} paydays land while it is under water. "
                f"That is a shortfall, not a timing gap."
            )
        return (
            f"Dips {self.depth} below the floor on {self.low_when} and recovers "
            f"by {self.recovers_on}. Moving {round_up_to(self.depth)} in before "
            f"{self.start} covers it."
        )


def find_dips(
    points: list[tuple[int, date, Decimal]],
    floor: Decimal,
    paycheck_days: list[int],
) -> list[Dip]:
    """Every run below `floor` on a path, with what it would take to bridge it.

    Takes `(day, date, balance)` triples rather than `PathPoint`s because the
    balances being judged are the *planned* ones — the baseline with the
    allocation superimposed — not the baseline the path object holds.
    """
    dips: list[Dip] = []
    open_dip: Dip | None = None

    for day, when, balance in points:
        if balance < floor:
            if open_dip is None:
                open_dip = Dip(
                    start=when,
                    start_day=day,
                    low=balance,
                    low_when=when,
                    depth=floor - balance,
                    recovers_on=None,
                    days_below=0,
                    paydays_below=0,
                )
            elif balance < open_dip.low:
                open_dip.low = balance
                open_dip.low_when = when
                open_dip.depth = floor - balance
        elif open_dip is not None:
            _close_dip(open_dip, when, day, paycheck_days)
            dips.append(open_dip)
            open_dip = None

    if open_dip is not None:
        # Still under water at the horizon: no recovery date, and the duration
        # runs to the end of what was modelled.
        end_day = points[-1][0]
        open_dip.days_below = end_day - open_dip.start_day
        open_dip.paydays_below = _paychecks_before(
            end_day, paycheck_days
        ) - _paychecks_before(open_dip.start_day, paycheck_days)
        open_dip.recovers_on = None
        dips.append(open_dip)

    for dip in dips:
        dip.low = dip.low.quantize(Decimal("0.01"))
        dip.depth = dip.depth.quantize(Decimal("0.01"))
    return dips


def _close_dip(
    dip: Dip, when: date, day: int, paycheck_days: list[int]
) -> None:
    dip.recovers_on = when
    dip.days_below = day - dip.start_day
    # Paydays that land *after* the dip opens and by the time it closes. A
    # payday on the opening day is already in that day's balance, so it did not
    # get a chance to help.
    dip.paydays_below = _paychecks_before(day, paycheck_days) - _paychecks_before(
        dip.start_day, paycheck_days
    )


def _dip_report(
    dip: Dip, account: str, account_name: str | None, floor: Decimal
) -> dict:
    return {
        "account": account,
        "account_name": account_name,
        "kind": dip.kind,
        "when": dip.start,
        "low_when": dip.low_when,
        "balance": dip.low,
        "floor": floor,
        # The measurement stays exact in `balance` and in the sentence; this
        # is the remedy, and a remedy is a transfer somebody makes.
        "one_off_needed": round_up_to(dip.depth),
        "recovers_on": dip.recovers_on,
        "days_below": dip.days_below,
        "paydays_below": dip.paydays_below,
        "why": dip.why,
    }


def required_rate(
    path: list[PathPoint],
    floor: Decimal,
    paycheck_days: list[int],
) -> tuple[Decimal, Decimal, date | None, str | None]:
    """The smallest per-paycheck contribution that keeps a path above its floor.

    Under a fixed contribution the balance is
    `baseline(t) + rate * paychecks_so_far(t)`, so each point demands
    `rate >= (floor - baseline(t)) / paychecks_so_far(t)` and the answer is
    whichever point demands most. Closed-form, so the search never has to
    re-run a forecast.

    A breach before the paychecks can accumulate cannot be solved by any rate —
    that needs a lump sum, and saying so is more use than returning an
    astronomical figure. One real bucket asked for +1,861 a paycheck to cover a
    dip nine days out.
    """
    needed = Decimal("0")
    low = None
    low_date = None
    warning = None

    for point in path:
        if low is None or point.balance < low:
            low = point.balance
            low_date = point.when
        if point.balance >= floor:
            continue
        shortfall = floor - point.balance
        landed = Decimal(_paychecks_before(point.day, paycheck_days))
        if landed < MIN_PAYCHECKS_TO_SOLVE:
            if warning is None:
                warning = (
                    f"Dips {shortfall.quantize(Decimal('0.01'))} below the floor "
                    f"on {point.when} — too soon to fix by contributing more. "
                    f"This needs a one-off top-up."
                )
            continue
        demand = shortfall / landed
        if demand > needed:
            needed = demand

    if low is None:
        low = Decimal("0")
    return (
        # Rounded up, not to nearest: this is a floor, and a minimum rounded
        # down is short by construction. Four cents of it was enough to fail
        # verification on a bucket whose rate was otherwise exactly right.
        needed.quantize(Decimal("0.01"), rounding=ROUND_CEILING),
        low.quantize(Decimal("0.01")),
        low_date,
        warning,
    )


def capacity_per_paycheck(
    path: list[PathPoint],
    buffer: Decimal,
    paycheck_days: list[int],
) -> tuple[Decimal, Decimal, dict | None, list[dict]]:
    """The largest total per paycheck the funding account can sustain.

    Returns two figures, because they answer different questions and the
    difference between them is the most useful thing the planner can say.

    `horizon` is what the year affords: the whole surplus divided across every
    payday. **This is the constraint on the plan.** `limited` is what the *path*
    affords, which is whichever point allows least — every point demands
    `total <= (baseline(t) - buffer) / paychecks_so_far(t)`.

    A plan between the two is not unaffordable, it is badly timed: the money
    exists over the year but is not there in the week it is needed. That wants a
    one-off transfer, not a smaller plan, and telling someone to cut their
    savings when they actually need to move 990 across for a fortnight is bad
    advice. So `limited` is advisory — the largest plan that needs no bridging
    at all — and the bridging schedule covers the difference.
    """
    limited = None
    binding: dict | None = None
    blocked: list[dict] = []

    for point in path:
        headroom = point.balance - buffer
        landed = Decimal(_paychecks_before(point.day, paycheck_days))
        if landed <= 0:
            if headroom < 0:
                blocked.append(
                    {
                        "when": point.when,
                        "balance": point.balance,
                        "short_by": (-headroom).quantize(Decimal("0.01")),
                    }
                )
            continue
        allowed = headroom / landed
        if limited is None or allowed < limited:
            limited = allowed
            binding = {
                "when": point.when,
                "balance": point.balance,
                "paychecks_by_then": int(landed),
            }

    if limited is None:
        limited = Decimal("0")
    if limited < 0:
        limited = Decimal("0")

    # What the year affords, ignoring when the money arrives.
    total_paychecks = Decimal(len(paycheck_days))
    if path and total_paychecks > 0:
        horizon = (path[-1].balance - buffer) / total_paychecks
    else:
        horizon = limited
    if horizon < 0:
        horizon = Decimal("0")

    return (
        limited.quantize(Decimal("0.01")),
        horizon.quantize(Decimal("0.01")),
        binding,
        blocked,
    )


def _funding_dips(
    path: list[PathPoint],
    total: Decimal,
    buffer: Decimal,
    paycheck_days: list[int],
) -> list[Dip]:
    """The dips a given per-paycheck total would leave in the funding account.

    Superposition again: a fixed total is a fixed transfer on known dates, so
    the balance under it is `baseline(t) - total * paychecks_so_far(t)` and no
    forecast has to be re-run to try a candidate.
    """
    points = [
        (
            point.day,
            point.when,
            point.balance - total * Decimal(_paychecks_before(point.day, paycheck_days)),
        )
        for point in path
    ]
    return find_dips(points, buffer, paycheck_days)


def allocatable_per_paycheck(
    path: list[PathPoint],
    buffer: Decimal,
    paycheck_days: list[int],
    path_capacity: Decimal,
    horizon_capacity: Decimal,
    max_bridges: int,
) -> Decimal:
    """The most that can be allocated while bridging stays occasional.

    Between the zero-bridge figure and the year's surplus there is a curve, and
    it has a knee. On real data: one transfer a year buys 120 a paycheck more
    than never bridging, three buy 216 — and then the count runs away, because
    a plan that allocates every last cent leaves checking with no slack at all
    and it goes under in every pay cycle.

    Found by bisection rather than a formula: dip *count* is a step function of
    the total, not something to solve for. Each candidate costs one arithmetic
    pass over the path. Adjacent dips can merge as the total rises, so the count
    is not perfectly monotonic and the search can settle a little low — which
    errs toward fewer transfers, the safe direction.
    """

    def acceptable(total: Decimal) -> bool:
        dips = _funding_dips(path, total, buffer, paycheck_days)
        # Count alone is not enough. A total high enough to hold the account
        # under water for half the year shows up as *one* dip, which would sail
        # through a budget of three. A structural dip disqualifies a candidate
        # however few there are of it.
        if any(dip.kind == "structural" for dip in dips):
            return False
        return len(dips) <= max_bridges

    if horizon_capacity <= path_capacity:
        return path_capacity
    if acceptable(horizon_capacity):
        return horizon_capacity

    lo, hi = path_capacity, horizon_capacity
    for _ in range(24):
        mid = (lo + hi) / 2
        if acceptable(mid):
            lo = mid
        else:
            hi = mid
    # Down, never to nearest. Rounding a boundary up by a cent is enough to buy
    # an extra dip — two cents under the floor is still under the floor.
    return lo.quantize(Decimal("0.01"), rounding=ROUND_FLOOR)


def rate_to_reach(
    path: list[PathPoint],
    target: Decimal,
    by: date | None,
    today: date,
    paycheck_days: list[int],
) -> Decimal:
    """The per-paycheck rate that gets a balance to `target` by `by`.

    With no date this is "hold at least `target` from here on", which is the
    same solve as a minimum against a higher line. With a date it is a single
    constraint at one point, which is a weaker demand — money that only has to
    be there by next August need not be there in October.
    """
    if by is None:
        needed, _, _, _ = required_rate(path, target, paycheck_days)
        return needed

    by_day = (by - today).days
    balance = None
    for point in path:
        if point.day <= by_day:
            balance = point.balance
        else:
            break
    if balance is None:
        balance = path[0].balance if path else Decimal("0")
    gap = target - balance
    if gap <= 0:
        return Decimal("0.00")
    landed = Decimal(_paychecks_before(by_day, paycheck_days))
    if landed < MIN_PAYCHECKS_TO_SOLVE:
        return Decimal("0.00")
    return (gap / landed).quantize(Decimal("0.01"), rounding=ROUND_CEILING)


def build_savings_plan(
    horizon_months: int = 12,
    window_months: int = 6,
    buffer: Decimal | None = None,
    today: date | None = None,
) -> SavingsPlan:
    """Produce a savings plan that provably works, or explain why none does."""
    from utils.dates import get_todays_date_timezone_adjusted

    today = today or get_todays_date_timezone_adjusted()
    buffer = DEFAULT_BUFFER if buffer is None else buffer
    end_date = today + timedelta(days=int(DAYS_PER_YEAR * horizon_months / 12))

    fund_id = funding_account_id()
    buckets = list(
        Bucket.objects.filter(active=True)
        .select_related("account", "reminder", "reminder__repeat")
        .order_by("priority", "id")
    )
    notes: list[str] = []

    if fund_id is None:
        return SavingsPlan(
            generated_for=today,
            horizon_months=horizon_months,
            buffer=buffer,
            paychecks=[],
            paychecks_in_horizon=0,
            capacity_per_paycheck=Decimal("0"),
            path_capacity_per_paycheck=Decimal("0"),
            horizon_capacity_per_paycheck=Decimal("0"),
            timing_shortfall=None,
            minimums_total=Decimal("0"),
            targets_total=Decimal("0"),
            planned_total=Decimal("0"),
            current_total=Decimal("0"),
            unallocated=Decimal("0"),
            freed_per_paycheck=Decimal("0"),
            optional_per_paycheck=Decimal("0"),
            feasible=False,
            verified=False,
            notes=[
                "No bucket has a linked reminder, so there is no funding "
                "account to plan against."
            ],
        )

    paychecks = pay_calendar(today, end_date, fund_id)
    if not paychecks:
        return SavingsPlan(
            generated_for=today,
            horizon_months=horizon_months,
            buffer=buffer,
            paychecks=[],
            paychecks_in_horizon=0,
            capacity_per_paycheck=Decimal("0"),
            path_capacity_per_paycheck=Decimal("0"),
            horizon_capacity_per_paycheck=Decimal("0"),
            timing_shortfall=None,
            minimums_total=Decimal("0"),
            targets_total=Decimal("0"),
            planned_total=Decimal("0"),
            current_total=Decimal("0"),
            unallocated=Decimal("0"),
            freed_per_paycheck=Decimal("0"),
            optional_per_paycheck=Decimal("0"),
            feasible=False,
            verified=False,
            notes=[
                "No income reminders on the funding account, so there is no pay "
                "calendar to plan against. Add a reminder for each paycheck."
            ],
        )
    paycheck_days = _paychecks_by_day(paychecks, today)

    # Every transfer the plan is deciding, so it can be lifted off both the
    # funding account and the buckets before anything is superimposed.
    plan_reminder_ids = {c.reminder_id for c in buckets if c.reminder_id}

    fund_path, _ = baseline_path(fund_id, today, end_date, plan_reminder_ids)
    # Three figures. The path one is what needs no bridging; the horizon one is
    # what the year affords and is the real test of affordability; `capacity` is
    # where the plan actually stops — the most that can be put away before the
    # bridging stops being occasional and turns into a fortnightly shuffle.
    path_capacity, horizon_capacity, binding, blocked = capacity_per_paycheck(
        fund_path, buffer, paycheck_days
    )
    max_bridges = max(1, round(MAX_BRIDGES_PER_YEAR * horizon_months / 12))
    capacity = allocatable_per_paycheck(
        fund_path,
        buffer,
        paycheck_days,
        path_capacity,
        horizon_capacity,
        max_bridges,
    )

    # One forecast pass per account, built here and shared. The rate solve, the
    # verification and the bridging solver must all reason about the same path.
    paths: dict[int, list[PathPoint]] = {
        c.id: bucket_path(c, today, end_date)
        for c in buckets
        if c.account_id
    }

    lines: list[BucketPlan] = []
    for bucket in buckets:
        lines.append(
            _line_for(
                bucket,
                today,
                end_date,
                paycheck_days,
                window_months,
                horizon_months,
                paths.get(bucket.id, []),
            )
        )

    minimums_total = sum((line.minimum_per_paycheck for line in lines), Decimal("0"))
    targets_total = sum((line.target_per_paycheck for line in lines), Decimal("0"))
    current_total = sum((line.current_per_paycheck for line in lines), Decimal("0"))
    other_funding_total = sum(
        (line.other_funding_per_paycheck for line in lines), Decimal("0")
    )

    if blocked:
        notes.append(
            f"The funding account drops below the {buffer} buffer on "
            f"{blocked[0]['when']} before any paycheck lands. No allocation can "
            f"fix that — it needs {blocked[0]['short_by']} put in now."
        )

    # Affordability is judged against the year, not against the bridging
    # budget: a minimum the household has stated gets funded even if it costs
    # more transfers than a discretionary top-up would be allowed to.
    feasible = minimums_total <= horizon_capacity
    if minimums_total > capacity and feasible:
        notes.append(
            f"The stated minimums come to "
            f"{minimums_total.quantize(Decimal('0.01'))} a paycheck, above the "
            f"{capacity} that keeps bridging down to {max_bridges} transfers. "
            f"They are funded anyway — a minimum is a commitment — so expect "
            f"more movements than that."
        )
        capacity = minimums_total
    if not feasible:
        levers = _levers(lines, minimums_total - horizon_capacity, horizon_capacity)
        for line in lines:
            line.planned_per_paycheck = Decimal("0.00")
        return SavingsPlan(
            generated_for=today,
            horizon_months=horizon_months,
            buffer=buffer,
            paychecks=paychecks,
            paychecks_in_horizon=len(paychecks),
            capacity_per_paycheck=capacity,
            path_capacity_per_paycheck=path_capacity,
            horizon_capacity_per_paycheck=horizon_capacity,
            timing_shortfall=None,
            minimums_total=minimums_total.quantize(Decimal("0.01")),
            targets_total=targets_total.quantize(Decimal("0.01")),
            planned_total=Decimal("0.00"),
            current_total=current_total.quantize(Decimal("0.01")),
            other_funding_total=other_funding_total.quantize(Decimal("0.01")),
            unallocated=Decimal("0.00"),
            freed_per_paycheck=Decimal("0.00"),
            optional_per_paycheck=Decimal("0.00"),
            feasible=False,
            verified=False,
            lines=lines,
            levers=levers,
            notes=notes
            + [
                "There is no valid plan: the minimum each account needs already "
                f"exceeds what can be allocated by "
                f"{(minimums_total - capacity).quantize(Decimal('0.01'))} a "
                "paycheck."
            ],
        )

    # Minimums first, then fill toward each target in priority order until the
    # money runs out. Order is what decides who goes short, which is why it is
    # stated rather than shared out equally.
    remaining = capacity - minimums_total
    for line in lines:
        line.planned_per_paycheck = line.minimum_per_paycheck
    for line in lines:
        want = line.target_per_paycheck - line.planned_per_paycheck
        if want <= 0:
            continue
        # Down to the increment. Rounding the discretionary half up is what
        # tips a plan past what the year affords, and going a little short of a
        # target is a preference not met rather than a bill not paid.
        give = round_down_to(min(want, remaining))
        if give <= 0:
            continue
        line.planned_per_paycheck = (line.planned_per_paycheck + give).quantize(
            Decimal("0.01")
        )
        remaining -= give
        if remaining <= 0:
            remaining = Decimal("0")
            break

    # The sweep: whatever survives goes to the accounts that exist to absorb it.
    sweeps = [
        line for line in lines if line.sweep
    ]
    # Divided by weight, not equally. Two accounts absorbing the leftover are
    # rarely equally deserving of it — a house-projects fund being propped up
    # and a child's savings account are not the same claim — and before there
    # was a way to say so, the split was decided by hand every time.
    total_share = sum((max(line.sweep_share, 0) for line in sweeps), 0)
    if remaining > 0 and total_share > 0:
        pot = remaining
        for line in sweeps:
            if line.sweep_share <= 0:
                continue
            share = round_down_to(pot * Decimal(line.sweep_share) / Decimal(total_share))
            if share <= 0:
                continue
            line.planned_per_paycheck = (
                line.planned_per_paycheck + share
            ).quantize(Decimal("0.01"))
            line.reason = (
                f"{share} a paycheck left over once everything else is funded"
                + (
                    f", {line.sweep_share} share of {total_share}."
                    if len(sweeps) > 1
                    else "."
                )
            )
            line.optional_per_paycheck = share
            remaining -= share

    planned_total = sum((line.planned_per_paycheck for line in lines), Decimal("0"))

    # Saving too much is a finding, not a happy accident. An account that
    # already has what it needs is money sitting still, and the planner is in a
    # better position than anyone to notice — it has just proved how little
    # each account actually requires.
    for line in lines:
        over = line.current_per_paycheck - line.planned_per_paycheck
        line.freed_per_paycheck = (
            over.quantize(Decimal("0.01")) if over > 0 else Decimal("0.00")
        )
        if line.freed_per_paycheck > 0:
            line.reason = (
                f"{line.reason} Putting in {line.current_per_paycheck} today, "
                f"which is {line.freed_per_paycheck} a paycheck more than this "
                f"needs."
            ).strip()

    freed_total = sum(
        (line.freed_per_paycheck for line in lines), Decimal("0")
    )
    optional_total = sum(
        (line.optional_per_paycheck for line in lines), Decimal("0")
    )

    breaches = _verify(lines, fund_path, paycheck_days, buffer, paths)
    bridges = solve_bridges(
        breaches, lines, paths, paycheck_days, fund_id, today
    )
    review = review_budgets(today)
    income = review_income(today, fund_id)

    # Say, per line, whether this bucket has been set up at all and whether
    # anything funds the spending it claims. The review already worked the
    # figures out, so this is a join rather than a second pass over the ledger.
    unbudgeted_by_bucket = {
        suggestion.bucket_name: suggestion
        for suggestion in review.suggestions
        if suggestion.kind == "create" and suggestion.bucket_name
    }
    for line in lines:
        suggestion = unbudgeted_by_bucket.get(line.bucket_name)
        if suggestion:
            line.unbudgeted_per_year = suggestion.measured_per_year
            line.coverage = (
                f"Claims {line.claimed_tag_count} "
                f"{'tag' if line.claimed_tag_count == 1 else 'tags'}, and "
                f"{suggestion.measured_per_year} a year of that spending has "
                f"no budget. The plan does not fund it until one says so."
            )
        elif line.claimed_tag_count:
            line.coverage = (
                f"Claims {line.claimed_tag_count} "
                f"{'tag' if line.claimed_tag_count == 1 else 'tags'}, all of it "
                f"either budgeted or already scheduled."
            )
        elif line.account_id:
            # Not an error — a bucket saving toward a goal genuinely owns no
            # spending. But it is the difference between "nothing to report"
            # and "nobody has looked", and those read identically otherwise.
            line.coverage = (
                "Claims no spending, so nothing here is checked against what "
                "this account actually spends."
            )

    # The bridge, taken from what verification actually measured rather than
    # re-derived from the binding point: the first timing dip on the funding
    # account, its date, and the amount that erases it.
    timing: dict | None = next(
        (
            b
            for b in breaches
            if b["account"] == "funding" and b["kind"] == "one_off"
        ),
        None,
    )
    if timing:
        notes.append(
            f"This plan is affordable over the year — it allocates "
            f"{planned_total.quantize(Decimal('0.01'))} a paycheck against "
            f"{horizon_capacity} the year affords — but the funding account "
            f"runs short "
            f"around {timing['when']}, recovering by {timing['recovers_on']}. "
            f"Moving {timing['one_off_needed']} into it beforehand covers the "
            f"gap; contributing less is not the fix."
        )
    if planned_total > path_capacity and binding:
        notes.append(
            f"A plan of {path_capacity} a paycheck or less would need no money "
            f"moved across at all — that is what the funding account can carry "
            f"unaided by {binding['when']}, {binding['paychecks_by_then']} "
            f"paychecks in."
        )
    if remaining >= ROUNDING_INCREMENT:
        notes.append(
            f"{remaining.quantize(Decimal('0.01'))} a paycheck is left unallocated "
            "— every goal is fully funded and no account is set to absorb the "
            "rest. That is money you do not need to save."
        )
    if optional_total > 0:
        sweep_names = ", ".join(
            line.bucket_name for line in lines if line.optional_per_paycheck > 0
        )
        notes.append(
            f"Every stated minimum and target is met by "
            f"{(planned_total - optional_total).quantize(Decimal('0.01'))} a "
            f"paycheck. The other {optional_total} goes to {sweep_names} "
            f"because nothing else asked for it — that is a goal you have not "
            f"written down, or money you could stop saving."
        )
    if freed_total > 0:
        cuts = sorted(
            (line for line in lines if line.freed_per_paycheck > 0),
            key=lambda line: line.freed_per_paycheck,
            reverse=True,
        )[:3]
        detail = ", ".join(
            f"{line.bucket_name} {line.freed_per_paycheck}" for line in cuts
        )
        notes.append(
            f"{freed_total.quantize(Decimal('0.01'))} a paycheck is going into "
            f"accounts that do not need it — {detail}. Lowering those "
            f"contributions costs nothing the plan depends on."
        )

    return SavingsPlan(
        generated_for=today,
        horizon_months=horizon_months,
        buffer=buffer,
        paychecks=paychecks,
        paychecks_in_horizon=len(paychecks),
        capacity_per_paycheck=capacity,
        path_capacity_per_paycheck=path_capacity,
        horizon_capacity_per_paycheck=horizon_capacity,
        timing_shortfall=timing,
        minimums_total=minimums_total.quantize(Decimal("0.01")),
        targets_total=targets_total.quantize(Decimal("0.01")),
        planned_total=planned_total.quantize(Decimal("0.01")),
        current_total=current_total.quantize(Decimal("0.01")),
        other_funding_total=other_funding_total.quantize(Decimal("0.01")),
        unallocated=remaining.quantize(Decimal("0.01")),
        freed_per_paycheck=freed_total.quantize(Decimal("0.01")),
        optional_per_paycheck=optional_total.quantize(Decimal("0.01")),
        feasible=True,
        verified=not any(b["kind"] == "structural" for b in breaches),
        lines=lines,
        breaches=breaches,
        bridges=bridges,
        budget_suggestions=review.suggestions,
        income_drift=income.drifts,
        notes=notes + review.notes,
    )


def reward_events(
    bucket: Bucket, today: date, end_date: date
) -> list[tuple[date, Decimal]]:
    """The November rewards, as money arriving in the account that gets them.

    A positive dated event rather than a smaller requirement, because the date
    is the whole point: the cards are cashed in a few weeks before Christmas,
    which is exactly when the gift bucket is at its emptiest. Money that shows
    up in November is worth far more to this plan than the same sum averaged
    across the year, and averaging it would ask the bucket to hold the full
    amount by December anyway.
    """
    if not bucket.receives_rewards:
        return []

    outlook = reward_outlook(today)
    if not outlook.redemption_on or outlook.expected_amount <= 0:
        return []
    if not (today <= outlook.redemption_on <= end_date):
        return []
    return [(outlook.redemption_on, outlook.expected_amount)]


@dataclass
class FundingSource:
    """One reminder that puts money into a bucket's account."""

    reminder_id: int
    description: str
    per_paycheck: Decimal
    # True for the one the plan decides. Everything else arrives whether the
    # plan likes it or not.
    adjustable: bool


def funding_sources(bucket: Bucket, per_year: Decimal) -> list[FundingSource]:
    """Every reminder that funds this bucket, not only the one it points at.

    Derived from the reminders themselves rather than declared on the bucket:
    a reminder whose destination is this account *is* funding it, so there is
    no way to forget to write one down. Ally - Kids is the case that demands
    it — the linked `Transfer to Kids` moves 85.00 a fortnight while an
    undeclared `DCA Transfer to Ally` moves 277.77, three times as much, and
    the page said the bucket received 85.

    Two kinds, and the difference is what the plan is allowed to do:

    - **adjustable** — the transfer the plan decides. `bucket.reminder`, and
      the only one lifted off the path so a new rate can be superimposed.
    - **fixed** — money that arrives regardless. A dependent-care transfer is
      set by an election made once a year, not by this plan. These stay *on*
      the path, which is why the solved rates were already right; what was
      missing was any way to see them.
    """
    if not bucket.account_id or per_year <= 0:
        return []

    sources: list[FundingSource] = []
    for reminder in (
        Reminder.objects.filter(reminder_destination_account_id=bucket.account_id)
        .select_related("repeat")
        .order_by("id")
    ):
        occurrences = occurrences_per_year(reminder.repeat)
        if not occurrences:
            # A one-off is a dated event on the path, not a rate. Reporting it
            # as one would imply it recurs.
            continue
        amount = abs(Decimal(str(reminder.amount or 0)))
        if amount <= 0:
            continue
        sources.append(
            FundingSource(
                reminder_id=reminder.id,
                description=reminder.description or f"Reminder {reminder.id}",
                per_paycheck=(amount * occurrences / per_year).quantize(
                    Decimal("0.01")
                ),
                adjustable=reminder.id == bucket.reminder_id,
            )
        )
    return sources


def bucket_path(
    bucket: Bucket, today: date, end_date: date
) -> list[PathPoint]:
    """The projected path of one bucket's account, unfunded by it.

    Shared deliberately. `_line_for` solves a rate against this path, `_verify`
    re-checks the finished plan on it, and the bridging solver asks it what it
    can spare — and all three have to be looking at the *same* path or the plan
    is proved against something it was not built from. That has already gone
    wrong once: verification excluded every bucket's transfer while the
    solver excluded only the row's own, and buckets carry each other's
    transfers, so the verified path was not the solved path.
    """
    # Children are already inside their parent's total, so a bucket linked to
    # both would fund that spending twice.
    budgets = spending_budgets(
        bucket.budgets.select_related("repeat", "parent").all()
    )
    spend_events: list[tuple[date, Decimal]] = []
    for budget in budgets:
        spend_events.extend(budget_events(budget, today, end_date))
    spend_events.extend(reward_events(bucket, today, end_date))

    path, _ = baseline_path(
        bucket.account_id,
        today,
        end_date,
        {bucket.reminder_id} if bucket.reminder_id else set(),
        spend_events=spend_events,
        # Only when budgets are supplying the spending; otherwise the recorded
        # reimbursements are the only evidence there is, and dropping them
        # would leave the account looking idle.
        replace_adhoc_reimbursements_to=(
            bucket.reminder.reminder_source_account_id
            if budgets and bucket.reminder_id
            else None
        ),
    )
    return path


def _line_for(
    bucket: Bucket,
    today: date,
    end_date: date,
    paycheck_days: list[int],
    window_months: int,
    horizon_months: int,
    path: list[PathPoint],
) -> BucketPlan:
    """Work out one bucket's minimum and target from its own account.

    Three inputs, in order of authority: the budgets it funds (what you plan to
    spend), the dated reminders on its account (what you are committed to), and
    the target balance (what you want it to build up to). Measured behaviour is
    reported but never planned on — that is the whole point of the budgets.
    """
    per_year = paychecks_per_year(bucket)
    current = bucket.contribution_per_paycheck or Decimal("0")
    stated_minimum = bucket.minimum_per_paycheck
    # Only for `analyze_account_trend`, which reads cleared history. A recorded
    # `Transaction` has no link back to the reminder that produced it — only
    # the forecast rows do — so the past can be matched by nothing but the
    # description. The path, which is all future, is matched by reminder id.
    own_description = (
        bucket.reminder.description
        if bucket.reminder_id and bucket.reminder.description
        else None
    )

    budgets = spending_budgets(
        bucket.budgets.select_related("repeat", "parent").all()
    )
    budgeted = sum(
        (budget_per_paycheck(b) for b in budgets), Decimal("0")
    ).quantize(Decimal("0.01"))
    budget_names = [b.name for b in budgets]

    if not bucket.account_id:
        minimum = stated_minimum if stated_minimum is not None else Decimal("0.00")
        return BucketPlan(
            bucket_id=bucket.id,
            bucket_name=bucket.name,
            account_id=None,
            account_name=None,
            priority=bucket.priority,
            sweep=bucket.sweep,
            sweep_share=bucket.sweep_share,
            lendable=bucket.lendable,
            receives_rewards=bucket.receives_rewards,
            paychecks_per_year=per_year,
            current_per_paycheck=current,
            minimum_per_paycheck=minimum,
            minimum_is_stated=stated_minimum is not None,
            target_per_paycheck=minimum,
            planned_per_paycheck=Decimal("0.00"),
            budgeted_per_paycheck=budgeted,
            budget_names=budget_names,
            target_balance=bucket.target_balance,
            projected_low=Decimal("0.00"),
            projected_low_date=None,
            observed_spend_per_month=Decimal("0.00"),
            spend_variance_per_paycheck=Decimal("0.00"),
            reason="No account linked, so there is nothing to project.",
            warning="Link an account to include this in the plan.",
        )

    # Everything funding this account, not only the reminder it points at.
    claimed_tag_count = bucket.claimed_tags().count()
    sources = funding_sources(bucket, per_year)
    other_funding = sum(
        (s.per_paycheck for s in sources if not s.adjustable), Decimal("0")
    ).quantize(Decimal("0.01"))
    other_funding_names = [s.description for s in sources if not s.adjustable]

    _, measured_per_year, measured_tag_names = tag_spend_events(
        bucket, today, end_date
    )
    rewards = reward_events(bucket, today, end_date)
    rewards_on = rewards[0][0] if rewards else None
    rewards_expected = rewards[0][1] if rewards else Decimal("0.00")

    # Solvency plus whatever cushion this bucket states. A floor of zero funds
    # the account to exactly nothing on its worst day, which is fine for a
    # bucket whose spending is all scheduled and thin for one whose spending is
    # budgeted — a budget is an estimate, and the buffer is what the estimate
    # being wrong costs. Zero by default, so this changes nothing until asked.
    derived, low, low_date, warning = required_rate(
        path, bucket.buffer or Decimal("0"), paycheck_days
    )
    # Up to the increment: this is a floor, and a floor rounded down is not one.
    # A stated minimum is rounded too — the user's figure is what it may not go
    # below, and going above it is always safe.
    minimum = round_up_to(max(derived, stated_minimum or Decimal("0")))
    # True only when the stated figure is the one *binding*, not merely when one
    # exists. Reporting "stated" for a minimum the arithmetic actually drove
    # made every line on this household's plan claim to be a stated floor,
    # including the ones the plan had worked out for itself.
    stated_is_binding = (
        stated_minimum is not None and stated_minimum >= derived
    )

    if bucket.sweep:
        target = minimum
        reason = "Takes whatever is left once everything else is funded."
    elif bucket.target_balance is not None:
        needed = rate_to_reach(
            path, bucket.target_balance, bucket.target_date, today,
            paycheck_days,
        )
        target = max(minimum, round_up_to(needed))
        reason = (
            f"Building to {bucket.target_balance}"
            + (f" by {bucket.target_date}" if bucket.target_date else "")
            + "."
        )
    elif budgets:
        target = minimum
        reason = "Covering " + ", ".join(budget_names) + "."
    else:
        target = minimum
        reason = "Covering its dated obligations."

    if stated_is_binding and stated_minimum > derived + ROUNDING_INCREMENT:
        note = (
            f"Your stated minimum of {stated_minimum} is holding this above "
            f"the {round_up_to(derived)} its budgets and bills actually "
            f"demand, so the figure here is your decision rather than a "
            f"calculation."
        )
        warning = f"{warning} {note}" if warning else note
    if other_funding > 0:
        # The plan is not being modest: this money is already on the path, so
        # the rate below it is what is needed *on top* of what arrives anyway.
        reason = (
            f"{reason} A further {other_funding} a paycheck arrives from "
            f"{', '.join(other_funding_names)}, which the plan does not set; "
            f"the figure here is what is needed on top of it."
        ).strip()
    if rewards_expected > 0:
        reason = (
            f"{reason} Card rewards of about {rewards_expected} are expected "
            f"on {rewards_on}, which is counted as money arriving rather than "
            f"money to save."
        ).strip()
    if measured_per_year > 0:
        # Reported, deliberately not funded. Budgets are the only thing the
        # plan acts on, so this is a case for changing a budget rather than a
        # number the plan quietly adopts — see `budget_review`.
        reason = (
            f"{reason} {measured_per_year} a year was spent on "
            f"{', '.join(measured_tag_names)} with no budget describing it; "
            f"the plan does not fund that until a budget says so."
        ).strip()

    # Measured behaviour, reported as a cross-check. A budget that disagrees
    # sharply with what the account actually spends is worth knowing about, but
    # it is the budget the plan is built on.
    trend = analyze_account_trend(
        bucket.account_id,
        months=window_months,
        source_account_id=(
            bucket.reminder.reminder_source_account_id
            if bucket.reminder_id
            else None
        ),
        today=today,
        contribution_description=own_description,
        horizon_months=horizon_months,
        per_year=per_year,
    )
    observed = trend.adhoc_flow_per_month if trend else Decimal("0.00")
    observed_per_paycheck = (
        (observed * 12 / per_year).quantize(Decimal("0.01"))
        if per_year > 0
        else Decimal("0.00")
    )
    variance = (budgeted + observed_per_paycheck).quantize(Decimal("0.01"))
    if budgets and not measured_tag_names and variance < -Decimal("25"):
        note = (
            f"Budgeted {budgeted} a paycheck, but this account has actually been "
            f"spending {abs(observed_per_paycheck)}. The plan follows the budget."
        )
        warning = f"{warning} {note}" if warning else note

    return BucketPlan(
        bucket_id=bucket.id,
        bucket_name=bucket.name,
        account_id=bucket.account_id,
        account_name=bucket.account.account_name,
        priority=bucket.priority,
        sweep=bucket.sweep,
        sweep_share=bucket.sweep_share,
        lendable=bucket.lendable,
        receives_rewards=bucket.receives_rewards,
        paychecks_per_year=per_year,
        current_per_paycheck=current,
        minimum_per_paycheck=minimum,
        minimum_is_stated=stated_is_binding,
        derived_minimum_per_paycheck=round_up_to(derived),
        target_per_paycheck=target,
        planned_per_paycheck=Decimal("0.00"),
        budgeted_per_paycheck=budgeted,
        budget_names=budget_names,
        measured_per_year=measured_per_year,
        measured_tag_names=measured_tag_names,
        rewards_expected=rewards_expected,
        rewards_on=rewards_on,
        other_funding_per_paycheck=other_funding,
        other_funding_names=other_funding_names,
        claimed_tag_count=claimed_tag_count,
        target_balance=bucket.target_balance,
        projected_low=low,
        projected_low_date=low_date,
        observed_spend_per_month=observed,
        spend_variance_per_paycheck=variance,
        reason=reason,
        warning=warning,
    )


def _verify(
    lines: list[BucketPlan],
    fund_path: list[PathPoint],
    paycheck_days: list[int],
    buffer: Decimal,
    paths: dict[int, list[PathPoint]],
) -> list[dict]:
    """Re-check the finished plan against every path it claims to satisfy.

    Superposition should make this redundant — the rates were derived from these
    very paths — but "should" is doing a lot of work in a module that decides
    where someone's money goes, and this has caught real arithmetic slips.

    What it is checking for is *not* "balance >= 0 everywhere". An account that
    dips and climbs back out has a timing problem, and the answer to a timing
    problem is to move money across, not to save less. Only a dip the account
    never recovers from — or one still open after two paydays have landed —
    means the plan itself is wrong. Every dip is reported either way, because
    the timing ones are the bridging schedule.
    """
    breaches: list[dict] = []

    total = sum((line.planned_per_paycheck for line in lines), Decimal("0"))
    planned_points = [
        (
            point.day,
            point.when,
            point.balance - total * Decimal(_paychecks_before(point.day, paycheck_days)),
        )
        for point in fund_path
    ]
    for dip in find_dips(planned_points, buffer, paycheck_days):
        breaches.append(_dip_report(dip, "funding", None, buffer))

    for line in lines:
        path = paths.get(line.bucket_id)
        if not line.account_id or not path:
            continue
        planned_points = [
            (
                point.day,
                point.when,
                point.balance
                + line.planned_per_paycheck
                * Decimal(_paychecks_before(point.day, paycheck_days)),
            )
            for point in path
        ]
        for dip in find_dips(planned_points, Decimal("0.00"), paycheck_days):
            breaches.append(
                _dip_report(dip, "bucket", line.account_name, Decimal("0.00"))
            )

    return breaches


def _source_rates(account_ids: list[int]) -> dict[int, Decimal]:
    """What each candidate account earns, for ranking which one to raid.

    A child account cannot hold an APY — the model forbids it, because the
    interest is calculated and paid on the parent. So a bucket's rate is its
    parent's rate, and sibling buckets all earn the same. Ranking by rate only
    separates accounts at different institutions, which is exactly when it
    matters: take the money that is working least hard.
    """
    rates: dict[int, Decimal] = {}
    for account in Account.objects.filter(pk__in=account_ids).select_related(
        "parent_account"
    ):
        rate = account.annual_rate or Decimal("0")
        if account.parent_account_id and not rate:
            rate = account.parent_account.annual_rate or Decimal("0")
        rates[account.pk] = rate
    return rates


def available_to_lend(
    path: list[PathPoint],
    rate_per_paycheck: Decimal,
    paycheck_days: list[int],
    from_day: int,
    until_day: int | None,
) -> Decimal:
    """The most this account can lend out over a window without going under.

    Superposition once more: money taken out on one date and put back on
    another shifts the account's balance down by that amount for the days in
    between, and by nothing at all outside them. So the loan is limited by the
    account's *lowest* balance while it is outstanding — not by what it holds on
    the day the money is wanted, which is the figure that would tempt you into
    emptying a bucket the week before its own bill lands.

    `until_day` of None is a permanent transfer: the account never gets it back,
    so every day to the horizon constrains it.
    """
    lowest: Decimal | None = None
    carried: Decimal | None = None

    for point in path:
        balance = point.balance + rate_per_paycheck * Decimal(
            _paychecks_before(point.day, paycheck_days)
        )
        if point.day < from_day:
            # A balance holds until something moves it. Windows are short — a
            # dip that lasts three days is the common case — and most accounts
            # have nothing scheduled inside one, so judging them only on points
            # that fall within it concluded that an account sitting on fifteen
            # thousand could not spare twenty-six.
            carried = balance
            continue
        if until_day is not None and point.day >= until_day:
            break
        if lowest is None or balance < lowest:
            lowest = balance

    if carried is not None and (lowest is None or carried < lowest):
        lowest = carried
    if lowest is None or lowest <= 0:
        return Decimal("0.00")
    return lowest.quantize(Decimal("0.01"), rounding=ROUND_FLOOR)


def solve_bridges(
    breaches: list[dict],
    lines: list[BucketPlan],
    paths: dict[int, list[PathPoint]],
    paycheck_days: list[int],
    funding_id: int,
    today: date,
) -> list[dict]:
    """Where the money for each timing dip comes from, and when it goes back.

    A plan is not "here is your allocation, and by the way watch out in
    October". It is an allocation plus a schedule of movements, and both are
    applied together. This is the second half.

    Every bridge is written as a **loan for exactly the length of the dip**.
    That falls out of the arithmetic rather than being a policy: paying the
    money back on the day the funding account recovers returns its path to
    precisely what it was, and the path from the recovery date onward was
    already proved to hold. So the repayment can never cause the next dip, and
    the source is only out of pocket for the days it actually has to be.

    Sources are ranked by what the money is earning, lowest first — raiding the
    least productive account is the right default, and it is the hook the
    interest-optimisation work will want. Ties break toward the least important
    bucket, then the one with the most to spare, so a big low-priority balance
    is preferred to scraping several small ones.

    A dip that cannot be funded is not a timing problem after all: it is
    reclassified `structural`, which is what makes the plan fail verification.
    That is the promise the dip classifier deliberately left open — depth never
    decides whether a dip is survivable, being able to cover it does.
    """
    bridges: list[dict] = []
    timing = [
        b
        for b in breaches
        if b["account"] == "funding" and b["kind"] == "one_off"
    ]
    if not timing:
        return bridges

    candidates = [
        line
        for line in lines
        if line.account_id and line.lendable and paths.get(line.bucket_id)
    ]
    protected = [
        line
        for line in lines
        if line.account_id and not line.lendable and paths.get(line.bucket_id)
    ]
    rates = _source_rates([line.account_id for line in candidates])

    for breach in timing:
        from_day = (breach["when"] - today).days
        until_day = (
            (breach["recovers_on"] - today).days if breach["recovers_on"] else None
        )
        # Already rounded up to the increment by `_dip_report`: covering all
        # but four dollars of a gap does not cover the gap.
        wanted = breach["one_off_needed"]

        offers = []
        for line in candidates:
            spare = available_to_lend(
                paths[line.bucket_id],
                line.planned_per_paycheck,
                paycheck_days,
                from_day,
                until_day,
            )
            if spare > 0:
                offers.append((rates.get(line.account_id, Decimal("0")), line, spare))
        offers.sort(key=lambda o: (o[0], -o[1].priority, -o[2]))

        movements: list[dict] = []
        outstanding = wanted
        for rate, line, spare in offers:
            if outstanding <= 0:
                break
            take = min(spare, outstanding)
            movements.append(
                {
                    "from_account_id": line.account_id,
                    "from_account": line.account_name,
                    "bucket_name": line.bucket_name,
                    "amount": take.quantize(Decimal("0.01")),
                    "annual_rate": rate,
                    "spare": spare,
                }
            )
            outstanding -= take

        bridge = {
            "for_account_id": funding_id,
            "when": breach["when"],
            "return_on": breach["recovers_on"],
            "amount": wanted,
            "covered": (wanted - outstanding).quantize(Decimal("0.01")),
            "shortfall": max(outstanding, Decimal("0")).quantize(Decimal("0.01")),
            "movements": movements,
        }
        if outstanding > 0:
            # Worth saying which protected account would have covered it — but
            # only after checking that it actually would. "Ellie's could have
            # paid for this" is a claim about her balance, not a turn of
            # phrase, and it has to be measured over the same window.
            held_back = [
                line.account_name
                for line in protected
                if available_to_lend(
                    paths[line.bucket_id],
                    line.planned_per_paycheck,
                    paycheck_days,
                    from_day,
                    until_day,
                )
                >= outstanding
            ]
            # No source can spare it, so calling this a timing problem would be
            # telling the user to make a transfer nobody can make.
            breach["kind"] = "structural"
            breach["why"] = (
                f"Needs {wanted} before {breach['when']}, and no account can "
                f"spare more than {bridge['covered']} of it while staying "
                f"solvent itself. That is not bad timing, it is a shortfall."
                + (
                    f" {', '.join(held_back)} could cover the rest but is "
                    f"marked not to be borrowed from."
                    if held_back
                    else ""
                )
            )
            bridge["why"] = breach["why"]
        else:
            names = ", ".join(
                f"{m['amount']} from {m['from_account']}" for m in movements
            )
            bridge["why"] = (
                f"Move {names} into checking before {breach['when']}"
                + (
                    f", back on {breach['recovers_on']}."
                    if breach["recovers_on"]
                    else "."
                )
            )
        bridges.append(bridge)

    return bridges


def _levers(
    lines: list[BucketPlan], shortfall: Decimal, capacity: Decimal
) -> list[dict]:
    """What could actually close an unfixable gap, biggest first.

    An infeasible plan is a finding, not a rounding error, so it gets the same
    treatment a planner would give it: here is the gap, here is what is driving
    it, here is what would have to change.
    """
    levers = [
        {
            "kind": "income",
            "what": "Increase income or reduce bills paid straight from checking",
            "amount_per_paycheck": shortfall.quantize(Decimal("0.01")),
            "detail": (
                f"Capacity is {capacity} a paycheck; the minimums need "
                f"{(capacity + shortfall).quantize(Decimal('0.01'))}."
            ),
        }
    ]
    for line in sorted(
        lines, key=lambda x: x.minimum_per_paycheck, reverse=True
    )[:5]:
        if line.minimum_per_paycheck <= 0:
            continue
        levers.append(
            {
                "kind": "minimum",
                "what": f"Reduce what {line.bucket_name} must hold",
                "amount_per_paycheck": line.minimum_per_paycheck,
                "detail": (
                    f"Stated minimum of {line.minimum_per_paycheck}"
                    if line.minimum_is_stated
                    else (
                        f"Driven by scheduled withdrawals; dips to "
                        f"{line.projected_low} on {line.projected_low_date}"
                    )
                ),
            }
        )
    return levers


def account_name_for(account_id: int | None) -> str | None:
    if account_id is None:
        return None
    account = Account.objects.filter(pk=account_id).first()
    return account.account_name if account else None
