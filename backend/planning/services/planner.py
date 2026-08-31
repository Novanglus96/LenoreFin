"""Trend analysis and contribution solving for the financial planner.

What an account does on its own, so a plan can be built against it.

What it measures, and deliberately nothing more:

1. `analyze_account_trend` measures what the account does on its own, from
   cleared history. "On its own" means with the contribution's own transfers
   removed — otherwise the contribution masks the very drift we are solving for,
   and a well-funded account looks healthy right up until you stop funding it.

2. `funding_account_id` and `paychecks_per_year` answer the two questions every
   caller needs about how the money moves.

Deciding what a contribution *should* be lives in `savings_plan`, which starts
from what there is to allocate rather than from what each account would like.
This module only measures; it no longer recommends.

Everything is Decimal end to end except the regression, which needs floats.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Q

from accounts.models import Account
from planning.models import Bucket
from transactions.models import Transaction, TransactionStatus
from transactions.services import get_account_transactions_and_balances
from utils.dates import get_todays_date_timezone_adjusted

# Average days per month/year, so a cadence in months and one in weeks are
# comparable without pretending every month is 30 days.
DAYS_PER_MONTH = Decimal("30.4375")
DAYS_PER_YEAR = Decimal("365.25")

# Below this many cleared transactions a trend is noise, not signal.
MIN_DATA_POINTS = 3

# A dip closer than this cannot meaningfully be fixed by changing a per-paycheck
# contribution — there are not enough paydays before it to accumulate anything.
MIN_PAYCHECKS_TO_SOLVE = Decimal("2")


@dataclass
class Trend:
    """What an account does when nobody is topping it up.

    `projected_flow_per_month` is what the solver uses, and it is deliberately
    not the historical figure. See `analyze_account_trend` for why.
    """

    natural_flow_per_month: Decimal      # historical, contributions removed
    scheduled_flow_per_month: Decimal    # forward, from the forecast
    adhoc_flow_per_month: Decimal        # historical spending no reminder explains
    projected_flow_per_month: Decimal    # scheduled + adhoc — the solver's input
    # The same figures in the cadence the money actually moves in. Planning
    # happens per paycheck, so a monthly rate is a unit the reader has to
    # convert before it means anything.
    paychecks_per_year: Decimal
    paychecks_in_horizon: Decimal
    scheduled_flow_per_paycheck: Decimal
    adhoc_flow_per_paycheck: Decimal
    projected_flow_per_paycheck: Decimal
    observed_slope_per_month: Decimal
    r_squared: float
    data_points: int
    window_months: int
    horizon_months: int
    current_balance: Decimal
    excluded_contribution_total: Decimal
    # Unscheduled spend seen only once in the window: reported, never projected.
    one_off_total: Decimal
    # Money added beyond the scheduled contribution — ad-hoc top-ups sharing its
    # description. Counted as real inflow, and surfaced so it is visible that a
    # bucket may only stay afloat because of them.
    extra_contributions_total: Decimal
    # The same top-ups expressed as a rate. This is *current funding*, not a
    # forecast: it says what is being put in today, by hand, on top of the
    # scheduled transfer. Nothing projects it forward — see
    # `adhoc_per_month` for why top-ups are excluded from the projection — but
    # leaving it out of the baseline was what made the planner demand hundreds
    # a paycheck of "new" money that was already being contributed.
    topup_per_paycheck: Decimal
    # The amount the contribution actually repeats at, which can differ from the
    # reminder's configured amount.
    modal_contribution_amount: Decimal | None
    # The low point of the projected balance path, and how many paychecks away
    # it is. A floor goal is solved against this, not against the endpoint.
    projected_low_balance: Decimal
    paychecks_to_low: Decimal
    # A floor derived from how much the account's spending actually varies —
    # offered as a starting point, never imposed.
    suggested_floor: Decimal


def _signed_amount(tx, account_id: int) -> Decimal:
    """Amount from this account's perspective: incoming positive, outgoing raw."""
    if tx.destination_account_id == account_id:
        return abs(tx.total_amount)
    return tx.total_amount


def _modal_contribution_amount(
    window: list,
    account_id: int,
    source_account_id: int | None,
    description: str | None,
) -> Decimal | None:
    """The amount this contribution *repeats* at, or None if nothing repeats.

    Real funding is a scheduled transfer plus ad-hoc top-ups sharing its
    description — 13 x 75.00 alongside one-off 850, 510, 1000. Only the
    repeating amount is the contribution; the rest is extra money genuinely
    added to the account.

    Derived from what recurred rather than from `reminder.amount`, which matters
    because applying a suggestion changes the reminder. A mode computed from
    history keeps describing history correctly, and shifts on its own as new
    transactions at the new amount accumulate.
    """
    if description is None:
        return None
    counts: dict[Decimal, int] = {}
    for tx in window:
        if not _matches_contribution_shape(
            tx, account_id, source_account_id, description
        ):
            continue
        amount = abs(tx.total_amount)
        counts[amount] = counts.get(amount, 0) + 1
    if not counts:
        return None
    amount, occurrences = max(counts.items(), key=lambda kv: (kv[1], kv[0]))
    # One occurrence is not a pattern; without repetition there is nothing to
    # separate a scheduled transfer from a top-up, so treat it all as the
    # contribution rather than inventing a distinction.
    return amount if occurrences >= 2 else None


def _matches_contribution_shape(
    tx,
    account_id: int,
    source_account_id: int | None,
    description: str | None,
) -> bool:
    """A transfer into this account, from the right place, under the right name."""
    if not tx.transaction_type or tx.transaction_type.slug != "transfer":
        return False
    if tx.destination_account_id != account_id:
        return False
    if source_account_id is not None and tx.source_account_id != source_account_id:
        return False
    if description is not None:
        return tx.description == description
    return True


def _is_contribution_transfer(
    tx,
    account_id: int,
    source_account_id: int | None,
    description: str | None = None,
    modal_amount: Decimal | None = None,
) -> bool:
    """True when this transaction is *this* contribution topping the account up.

    Real transactions carry no FK back to the reminder that spawned them, so the
    contribution is identified by its shape: a transfer landing in this account.

    Matching on the source account alone is not enough. One account is very
    often fed by several transfers from the same checking account — only one of
    which is the contribution being solved for. Excluding all of them drops the
    others out of the natural flow *without* crediting them back, so the account
    looks like it drains far faster than it does and the suggestion balloons.

    The reminder's description is the discriminator, because the transaction
    generator copies it verbatim onto every transaction it creates. It is also
    stable across amount changes, which matters because applying a suggestion
    changes the amount — an amount-based match would break itself on first use.

    Without a linked reminder there is nothing to match on, so any incoming
    transfer is treated as a top-up. That is coarse, and it is why linking the
    reminder is worth doing.
    """
    if not _matches_contribution_shape(
        tx, account_id, source_account_id, description
    ):
        return False
    # Only the repeating amount is the scheduled contribution. Extra top-ups
    # under the same description are real money arriving, and excluding them
    # made every bucket look like it was draining when it was growing.
    if modal_amount is not None:
        return abs(tx.total_amount) == modal_amount
    return True


def _linear_regression(points: list[tuple[float, float]]) -> tuple[float, float]:
    """Least-squares slope (per day) and r² over (day_offset, balance) points."""
    n = len(points)
    if n < 2:
        return 0.0, 0.0
    mean_x = sum(p[0] for p in points) / n
    mean_y = sum(p[1] for p in points) / n
    sxx = sum((p[0] - mean_x) ** 2 for p in points)
    if sxx == 0:
        return 0.0, 0.0
    sxy = sum((p[0] - mean_x) * (p[1] - mean_y) for p in points)
    slope = sxy / sxx
    syy = sum((p[1] - mean_y) ** 2 for p in points)
    r_squared = (sxy**2) / (sxx * syy) if syy else 0.0
    return slope, r_squared


def _scheduled_flow(
    account_id: int,
    horizon_months: int,
    today: date,
    contribution_description: str | None,
) -> tuple[Decimal, set[str], list[tuple[int, Decimal]]]:
    """Net monthly flow, the descriptions it covers, and the balance path.

    The path is (days from today, projected balance) and is what a floor goal
    has to be solved against — an account can finish the year comfortably
    having gone negative in month three, and only the path shows that.

    The description set is how the caller avoids double counting: anything the
    forecast will generate forward — reminder transactions, projected interest,
    credit-card payments — must not *also* be counted from history.

    History alone gets lumpy obligations wrong. One real savings bucket carries
    an annual -687 and a quarterly -2036.92; whether those land inside a
    six-month window is luck, and the answer swung by 157 a paycheck — in the
    opposite direction — depending on how they fell. The forecast knows their
    actual calendar placement, so it weights them properly.

    Direction cannot be read off forecast rows (`totals_only` strips source and
    destination accounts), so net change comes from the running balance and the
    contribution's own inflows are subtracted by description.
    """
    end_date = today + timedelta(days=int(DAYS_PER_YEAR) * horizon_months // 12)
    try:
        rows, opening = get_account_transactions_and_balances(
            end_date, account_id, True, True, today, False
        )
    except Exception:
        # A forecast failure must not take the whole planner down; returning
        # zero leaves the caller with history only, i.e. the old behaviour.
        return Decimal("0"), set(), []
    if not rows:
        return Decimal("0"), set(), []

    def field(row, name):
        return row[name] if isinstance(row, dict) else getattr(row, name, None)

    covered: set[str] = set()
    path: list[tuple[int, Decimal]] = []
    # Rows carry no source/destination (totals_only strips them), so a row's
    # signed effect is read from the step it makes in the running balance.
    previous = Decimal(str(opening))
    scheduled_total = Decimal("0")
    for row in rows:
        description = field(row, "description")
        row_date = field(row, "transaction_date")
        row_balance = field(row, "balance")
        delta = Decimal("0")
        if row_balance is not None:
            balance = Decimal(str(row_balance))
            delta = balance - previous
            previous = balance
            if row_date is not None:
                path.append(((row_date - today).days, balance))
        # Only *simulated* rows are recurring projections. A real future-dated
        # transaction that happens to share a description is a one-off already
        # on the books, and letting it into this set was catastrophic: a single
        # future "Car Transfer" row suppressed all six historical ones, wiping
        # that bucket's entire ad-hoc rate and asking for 30 a paycheck less
        # than it needs.
        simulated = bool(field(row, "simulated"))
        if description and simulated:
            covered.add(description)

        # The rate counts recurring projections only. A real future-dated
        # transaction is a known one-off, and for these accounts it is usually
        # the same behaviour the ad-hoc rate already carries forward — counting
        # both charged an account twice for one habit and inflated its shortfall
        # by hundreds a month. It still sits in `path`, so a floor goal sees the
        # dip it causes.
        if not simulated:
            continue
        if (
            contribution_description is not None
            and description == contribution_description
        ):
            continue
        scheduled_total += delta

    per_month = (scheduled_total / Decimal(horizon_months)).quantize(Decimal("0.01"))
    return per_month, covered, path


def analyze_account_trend(
    account_id: int,
    months: int = 6,
    source_account_id: int | None = None,
    today: date | None = None,
    contribution_description: str | None = None,
    horizon_months: int = 12,
    per_year: Decimal | None = None,
) -> Trend | None:
    """Measure an account's natural drift over the last `months` months.

    Returns None when the account does not exist or the window holds too little
    cleared history to say anything honest about.
    """
    if not Account.objects.filter(pk=account_id).exists():
        return None
    account = Account.objects.get(pk=account_id)

    try:
        cleared = TransactionStatus.objects.get(slug="cleared")
    except TransactionStatus.DoesNotExist:
        return None

    today = today or get_todays_date_timezone_adjusted()
    start_date = today - timedelta(days=int(DAYS_PER_MONTH) * months)

    account_q = Q(source_account_id=account_id) | Q(destination_account_id=account_id)
    base = Transaction.objects.filter(account_q, status=cleared)

    # Balance at the window's start: everything that cleared before it.
    opening = (account.opening_balance or Decimal("0")) + (
        account.archive_balance or Decimal("0")
    )
    balance_at_start = opening
    for tx in base.filter(transaction_date__lt=start_date).select_related(
        "transaction_type"
    ):
        balance_at_start += _signed_amount(tx, account_id)

    window = list(
        base.filter(
            transaction_date__gte=start_date, transaction_date__lte=today
        )
        .select_related("transaction_type")
        .order_by("transaction_date", "id")
    )
    if len(window) < MIN_DATA_POINTS:
        return None

    scheduled_per_month, forecast_descriptions, forecast_path = _scheduled_flow(
        account_id, horizon_months, today, contribution_description
    )

    # Walk the window once, splitting flows three ways while accumulating the
    # real balance curve for the regression.
    modal_amount = _modal_contribution_amount(
        window, account_id, source_account_id, contribution_description
    )

    natural_flow = Decimal("0")
    contributed = Decimal("0")
    extra_contributions = Decimal("0")
    # Ad-hoc candidates are gathered per description so one-offs can be dropped
    # afterwards — see below.
    adhoc_by_description: dict[str, list[Decimal]] = {}
    balance = balance_at_start
    points: list[tuple[float, float]] = []
    for tx in window:
        amount = _signed_amount(tx, account_id)
        balance += amount
        if _is_contribution_transfer(
            tx, account_id, source_account_id, contribution_description, modal_amount
        ):
            contributed += amount
        else:
            natural_flow += amount
            if (
                _matches_contribution_shape(
                    tx, account_id, source_account_id, contribution_description
                )
                or (
                    contribution_description is not None
                    and tx.description == contribution_description
                )
            ):
                # An extra top-up: real inflow, but not the scheduled stream.
                # The second arm matters — a transfer recorded under some other
                # transaction type still fails the shape check, and would then
                # hit the forecast-description guard below and be dropped
                # entirely. That silently deleted 1,441 of real funding from one
                # bucket, making it look like it was draining.
                extra_contributions += amount
            elif tx.description not in forecast_descriptions:
                adhoc_by_description.setdefault(tx.description, []).append(amount)
        points.append(((tx.transaction_date - start_date).days, float(balance)))

    # A description seen exactly once in the window is an *event*, not a rate.
    # Real data settles this: one savings bucket's entire unscheduled history
    # was "Closing Costs" and "Home Transfer", one occurrence each. Treating
    # 5,654 of house-purchase costs as a recurring monthly burn asked for an
    # extra 573 a paycheck forever. Meanwhile the grocery bucket's unscheduled
    # history is nine "Groceries Transfer" rows, which genuinely is a rate.
    adhoc_flow = sum(
        (sum(amounts) for amounts in adhoc_by_description.values() if len(amounts) > 1),
        Decimal("0"),
    )
    one_off_total = sum(
        (sum(amounts) for amounts in adhoc_by_description.values() if len(amounts) == 1),
        Decimal("0"),
    )

    slope_per_day, r_squared = _linear_regression(points)
    window_days = Decimal((today - start_date).days or 1)
    months_elapsed = window_days / DAYS_PER_MONTH

    # Top-ups are deliberately NOT projected. They are unplanned — money moved
    # in when it happened to be spare — so counting on them would quietly build
    # the plan on rescues that may not come, and hide the fact that the
    # *scheduled* transfer is short. They are reported instead, as
    # `extra_contributions_total`.
    adhoc_per_month = (adhoc_flow / months_elapsed).quantize(Decimal("0.01"))
    # Biweekly unless a linked reminder says otherwise — the overwhelmingly
    # common case, and the only sane guess when nothing is linked.
    per_year = per_year if per_year is not None else Decimal("26")
    horizon_paychecks = (per_year * Decimal(horizon_months) / 12).quantize(
        Decimal("0.01")
    )
    projected_per_month = scheduled_per_month + adhoc_per_month

    # Top-ups as a rate over the window that actually contained them. Measured
    # against paychecks rather than months so it is directly comparable with
    # `per_paycheck`, which is what it gets added to.
    window_paychecks = window_days / DAYS_PER_YEAR * per_year
    topup_per_paycheck = (
        (extra_contributions / window_paychecks).quantize(Decimal("0.01"))
        if window_paychecks > 0
        else Decimal("0.00")
    )

    # Overlay ad-hoc spending on the forecast path. The forecast only knows
    # scheduled flows, so for a bucket like groceries — which has no outflow
    # reminder at all — the raw path climbs forever and would report a low point
    # of "today", hiding the very dip a floor goal exists to prevent.
    low_balance = balance
    days_to_low = 0
    adhoc_per_day = adhoc_per_month / DAYS_PER_MONTH
    for days, projected in forecast_path:
        adjusted = projected + adhoc_per_day * Decimal(days)
        if adjusted < low_balance:
            low_balance = adjusted
            days_to_low = days

    # How much worse a bad cycle is than a typical one. The buffer exists to
    # absorb *variation*, so it is sized to the excess of the worst month over
    # the average — not to the worst month outright, which for a pass-through
    # bucket like groceries would demand holding a whole month's spend idle.
    monthly_totals: dict[int, Decimal] = {}
    for tx in window:
        if _is_contribution_transfer(
            tx, account_id, source_account_id, contribution_description
        ):
            continue
        bucket = (today - tx.transaction_date).days // int(DAYS_PER_MONTH)
        monthly_totals.setdefault(bucket, Decimal("0"))
        monthly_totals[bucket] += _signed_amount(tx, account_id)
    if monthly_totals:
        worst_month = min(monthly_totals.values())
        mean_month = sum(monthly_totals.values()) / Decimal(len(monthly_totals))
        suggested_floor = abs(worst_month - mean_month).quantize(Decimal("0.01"))
    else:
        suggested_floor = Decimal("0.00")

    return Trend(
        natural_flow_per_month=(natural_flow / months_elapsed).quantize(
            Decimal("0.01")
        ),
        scheduled_flow_per_month=scheduled_per_month,
        adhoc_flow_per_month=adhoc_per_month,
        projected_flow_per_month=projected_per_month,
        paychecks_per_year=per_year,
        paychecks_in_horizon=horizon_paychecks,
        # Quantized here, not in _per_paycheck: the solver wants full precision,
        # but these are serialised, and an unbounded division through a
        # condecimal(decimal_places=2) is a 500 waiting to happen.
        scheduled_flow_per_paycheck=_per_paycheck(
            scheduled_per_month, per_year
        ).quantize(Decimal("0.01")),
        adhoc_flow_per_paycheck=_per_paycheck(adhoc_per_month, per_year).quantize(
            Decimal("0.01")
        ),
        projected_flow_per_paycheck=_per_paycheck(
            projected_per_month, per_year
        ).quantize(Decimal("0.01")),
        horizon_months=horizon_months,
        observed_slope_per_month=(
            Decimal(str(slope_per_day)) * DAYS_PER_MONTH
        ).quantize(Decimal("0.01")),
        r_squared=round(r_squared, 4),
        data_points=len(window),
        window_months=months,
        current_balance=balance.quantize(Decimal("0.01")),
        excluded_contribution_total=contributed.quantize(Decimal("0.01")),
        one_off_total=one_off_total.quantize(Decimal("0.01")),
        extra_contributions_total=extra_contributions.quantize(Decimal("0.01")),
        topup_per_paycheck=topup_per_paycheck,
        modal_contribution_amount=modal_amount,
        projected_low_balance=low_balance.quantize(Decimal("0.01")),
        paychecks_to_low=(
            Decimal(days_to_low) / DAYS_PER_YEAR * per_year
        ).quantize(Decimal("0.01")),
        suggested_floor=suggested_floor,
    )


def occurrences_per_year(repeat) -> Decimal | None:
    """How many times a year a repeat period comes round.

    None when the repeat is missing or degenerate, so callers can pick their own
    fallback rather than inheriting a guess that looks like a measurement.
    """
    if repeat is None:
        return None
    period_days = (
        Decimal(repeat.days or 0)
        + Decimal(repeat.weeks or 0) * 7
        + Decimal(repeat.months or 0) * DAYS_PER_MONTH
        + Decimal(repeat.years or 0) * DAYS_PER_YEAR
    )
    if period_days <= 0:
        return None
    # Quantized because the raw division is unbounded (365.25/14 runs to 27
    # decimal places) and this value is serialised as well as multiplied.
    # Four places is far finer than any cadence distinction that matters.
    return (DAYS_PER_YEAR / period_days).quantize(Decimal("0.0001"))


def paychecks_per_year(bucket: Bucket) -> Decimal:
    """How many times a year this bucket's contribution is paid.

    Derived from the linked reminder's repeat rather than a global payday
    setting, so two buckets on different cadences each solve correctly. Falls
    back to biweekly, which is the overwhelmingly common case and the only sane
    guess when nothing is linked.
    """
    biweekly = Decimal("26")
    reminder = bucket.reminder
    if not reminder:
        return biweekly
    return occurrences_per_year(reminder.repeat) or biweekly


def _per_paycheck(monthly: Decimal, per_year: Decimal) -> Decimal:
    """Convert a monthly figure to a per-paycheck one at this cadence."""
    if per_year <= 0:
        return Decimal("0")
    return (monthly * 12) / per_year


def funding_account_id() -> int | None:
    """The account the contributions are paid out of.

    Taken as the one most buckets draw on rather than configured separately,
    because that is already recorded on every linked reminder.
    """
    counts: dict[int, int] = {}
    for c in Bucket.objects.filter(
        active=True, reminder__isnull=False
    ).select_related("reminder"):
        source = c.reminder.reminder_source_account_id
        if source:
            counts[source] = counts.get(source, 0) + 1
    if not counts:
        return None
    return max(counts.items(), key=lambda kv: kv[1])[0]
