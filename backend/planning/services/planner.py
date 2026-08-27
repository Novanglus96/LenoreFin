"""Trend analysis and contribution solving for the financial planner.

The question this answers is the one you actually ask about a savings account:
"this is drifting the wrong way — how much more per paycheck fixes it?"

Answering it takes three steps, deliberately kept separate:

1. `analyze_account_trend` measures what the account does on its own, from
   cleared history. "On its own" means with the contribution's own transfers
   removed — otherwise the contribution masks the very drift we are solving for,
   and a well-funded account looks healthy right up until you stop funding it.

2. `solve_for_contribution` turns a goal into a required per-paycheck figure,
   using the natural flow from step 1 and the cadence of the linked reminder.

3. `project_with_contribution` superimposes the change on the existing forecast
   so the suggestion can be shown against a curve rather than asserted.

Everything is Decimal end to end except the regression, which needs floats.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.db.models import Q

from accounts.models import Account
from planning.models import Contribution
from reminders.models import Reminder
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


@dataclass
class Suggestion:
    """A per-paycheck figure, and everything needed to judge it."""

    goal_type: str
    current_per_paycheck: Decimal
    required_per_paycheck: Decimal
    delta_per_paycheck: Decimal
    paychecks_per_year: Decimal
    reason: str
    achievable: bool = True
    warning: str | None = None


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


def paychecks_per_year(contribution: Contribution) -> Decimal:
    """How many times a year this contribution is paid.

    Derived from the linked reminder's repeat rather than a global payday
    setting, so two contributions on different cadences each solve correctly.
    Falls back to biweekly, which is the overwhelmingly common case and the
    only sane guess when nothing is linked.
    """
    biweekly = Decimal("26")
    reminder = contribution.reminder
    if not reminder:
        return biweekly
    return occurrences_per_year(reminder.repeat) or biweekly


def _per_paycheck(monthly: Decimal, per_year: Decimal) -> Decimal:
    """Convert a monthly figure to a per-paycheck one at this cadence."""
    if per_year <= 0:
        return Decimal("0")
    return (monthly * 12) / per_year


# Goals you state rather than derive. They need no history at all, so they are
# answerable on an account the planner cannot measure.
PRESCRIPTIVE_GOALS = frozenset(
    {Contribution.GOAL_BUDGET, Contribution.GOAL_MAXIMISE}
)


def solve_for_contribution(
    contribution: Contribution,
    trend: Trend | None,
    today: date | None = None,
) -> Suggestion | None:
    """Turn a goal into a required per-paycheck figure.

    Returns None for a contribution with no goal, and for a descriptive goal on
    an account with too little history to measure — those genuinely have no
    answer. Prescriptive goals still resolve without a trend.
    """
    goal = contribution.goal_type
    if goal == Contribution.GOAL_NONE:
        return None
    if trend is None and goal not in PRESCRIPTIVE_GOALS:
        return None

    today = today or get_todays_date_timezone_adjusted()
    per_year = paychecks_per_year(contribution)
    current = contribution.per_paycheck or Decimal("0")

    # The account's own drift, expressed in the same units as a contribution.
    # Projected, not historical: scheduled obligations come from the forecast so
    # annual and quarterly lumps are weighted by their real calendar placement,
    # and ad-hoc spending comes from history because no reminder describes it.
    natural = (
        _per_paycheck(trend.projected_flow_per_month, per_year)
        if trend is not None
        else Decimal("0")
    )

    warning = None
    achievable = True

    if goal == Contribution.GOAL_BUDGET:
        # Prescriptive: you decided what this is worth per year, so history does
        # not get a vote. Deliberately ignores drift — the point of a budget is
        # that it constrains spending rather than following it.
        required = contribution.goal_amount / per_year
        reason = (
            f"Funding {contribution.goal_amount} a year over "
            f"{per_year.quantize(Decimal('0.1'))} paychecks."
        )

    elif goal == Contribution.GOAL_MAXIMISE:
        # Cannot be solved here: it depends on every *other* contribution being
        # funded first. The caller does a second pass once the rest are known —
        # see `apply_maximise_goals`. Reported as current until then, so a
        # half-computed figure is never mistaken for an answer.
        return Suggestion(
            goal_type=goal,
            current_per_paycheck=current,
            required_per_paycheck=current,
            delta_per_paycheck=Decimal("0"),
            paychecks_per_year=per_year,
            reason="Takes whatever is left after the other goals are funded.",
            achievable=True,
            warning=None,
        )

    elif goal == Contribution.GOAL_HOLD:
        # Offset the drift exactly: contribution + natural == 0.
        required = -natural
        reason = (
            f"Projected at {trend.projected_flow_per_month}/month against this "
            f"account; {required.quantize(Decimal('0.01'))} per paycheck holds it flat."
        )

    elif goal == Contribution.GOAL_GROW:
        # A rate compounds off the balance; an amount is flat. Rate wins when set.
        if contribution.goal_rate:
            monthly_growth = (
                trend.current_balance * (contribution.goal_rate / 100)
            ) / 12
            target_desc = f"{contribution.goal_rate}%/yr"
        else:
            monthly_growth = contribution.goal_amount
            target_desc = f"{contribution.goal_amount}/month"
        required = -natural + _per_paycheck(monthly_growth, per_year)
        reason = (
            f"Offsetting {trend.projected_flow_per_month}/month of drift and "
            f"growing by {target_desc}."
        )

    elif goal == Contribution.GOAL_TARGET:
        if not contribution.goal_date:
            return None
        days_left = (contribution.goal_date - today).days
        if days_left <= 0:
            return Suggestion(
                goal_type=goal,
                current_per_paycheck=current,
                required_per_paycheck=current,
                delta_per_paycheck=Decimal("0"),
                paychecks_per_year=per_year,
                reason="The target date has already passed.",
                achievable=False,
                warning="Set a future target date to get a suggestion.",
            )
        paychecks_left = (Decimal(days_left) / DAYS_PER_YEAR) * per_year
        if paychecks_left < 1:
            paychecks_left = Decimal("1")
        gap = contribution.goal_amount - trend.current_balance
        # Each remaining paycheck must cover its share of the gap *and* offset
        # the drift that will happen between now and then.
        required = (gap / paychecks_left) - natural
        reason = (
            f"{gap.quantize(Decimal('0.01'))} short of "
            f"{contribution.goal_amount} with "
            f"{paychecks_left.quantize(Decimal('0.1'))} paychecks to go."
        )

    elif goal == Contribution.GOAL_FLOOR:
        # A floor binds at the account's *low point*, not at the end of the
        # horizon. An account can finish the year healthy having gone under in
        # month three, and the endpoint would never show it.
        low = trend.projected_low_balance
        floor = contribution.goal_amount
        if low >= floor:
            required = current
            reason = (
                f"Dips to {low} at worst, staying above the {floor} floor."
            )
        else:
            shortfall = floor - low
            paychecks_before_low = trend.paychecks_to_low
            if paychecks_before_low < MIN_PAYCHECKS_TO_SOLVE:
                # Too close to fix by changing the rate. Only a couple of
                # paychecks land before the dip, so dividing the shortfall by
                # them demands an absurd figure — one real bucket asked for
                # +1,861 a paycheck to cover a dip nine days out. A lump sum is
                # the honest answer, and the rate is left alone.
                required = current
                reason = (
                    f"Dips to {low} in only "
                    f"{paychecks_before_low.quantize(Decimal('0.1'))} paychecks — "
                    f"too soon to fix by contributing more."
                )
                warning = (
                    f"Needs a one-off top-up of about "
                    f"{shortfall.quantize(Decimal('0.01'))} rather than a "
                    f"per-paycheck change."
                )
            else:
                # Only the paychecks landing *before* the dip can fix it;
                # spreading it over the whole horizon would arrive too late.
                required = current + (shortfall / paychecks_before_low)
                reason = (
                    f"Dips to {low} in "
                    f"{paychecks_before_low.quantize(Decimal('0.1'))} paychecks, "
                    f"{shortfall.quantize(Decimal('0.01'))} under the {floor} floor."
                )

    else:
        return None

    try:
        required = required.quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError):
        return None

    if required < 0:
        # A negative requirement means the account funds itself; suggesting a
        # negative transfer would be nonsense, so floor it and say why.
        warning = (
            "This account grows on its own — the contribution could stop "
            "entirely and still meet the goal."
        )
        required = Decimal("0.00")

    if trend is not None and trend.extra_contributions_total > 0:
        # The gap between the scheduled transfer and what the account needs has
        # been covered by hand. Naming it turns "you are short" into "this is
        # what you have been topping up, and this is what would replace it".
        topped_up = trend.extra_contributions_total
        note = (
            f"You topped this up by {topped_up} over the last "
            f"{trend.window_months} months; this figure does not assume that "
            f"continues."
        )
        warning = f"{warning} {note}" if warning else note

    return Suggestion(
        goal_type=goal,
        current_per_paycheck=current,
        required_per_paycheck=required,
        delta_per_paycheck=(required - current).quantize(Decimal("0.01")),
        paychecks_per_year=per_year,
        reason=reason,
        achievable=achievable,
        warning=warning,
    )


def project_with_contribution(
    trend: Trend,
    suggestion: Suggestion,
    months: int = 12,
) -> list[tuple[int, Decimal, Decimal]]:
    """Month-by-month balance under the current vs the suggested contribution.

    Superimposes the change on the measured trend rather than re-running the
    forecast engine with an override: the contribution is a fixed transfer, so
    the difference between the two curves is linear in the delta. This does not
    compound, so on an interest-bearing account the suggested curve is a slight
    under-estimate — which is the safe direction to be wrong in.

    Returns (month_offset, balance_now, balance_if_applied) tuples.
    """
    per_year = suggestion.paychecks_per_year
    monthly_natural = trend.projected_flow_per_month
    monthly_current = (suggestion.current_per_paycheck * per_year) / 12
    monthly_suggested = (suggestion.required_per_paycheck * per_year) / 12

    rows = []
    for m in range(months + 1):
        now = trend.current_balance + (monthly_natural + monthly_current) * m
        applied = trend.current_balance + (monthly_natural + monthly_suggested) * m
        rows.append(
            (m, now.quantize(Decimal("0.01")), applied.quantize(Decimal("0.01")))
        )
    return rows


def analyze_contribution(
    contribution: Contribution,
    months: int = 6,
    today: date | None = None,
    horizon_months: int = 12,
) -> dict | None:
    """Full picture for one contribution: trend, suggestion, and drift.

    Returns None when the contribution has no account to measure.
    """
    if not contribution.account_id:
        return None

    source_account_id = (
        contribution.reminder.reminder_source_account_id
        if contribution.reminder_id
        else None
    )
    trend = analyze_account_trend(
        contribution.account_id,
        months=months,
        source_account_id=source_account_id,
        today=today,
        contribution_description=(
            contribution.reminder.description if contribution.reminder_id else None
        ),
        horizon_months=horizon_months,
        per_year=paychecks_per_year(contribution),
    )
    if trend is None:
        # A prescriptive goal still has an answer here — it never depended on
        # the history that is missing.
        return {
            "contribution_id": contribution.id,
            "account_id": contribution.account_id,
            "trend": None,
            "suggestion": solve_for_contribution(contribution, None, today=today),
            "drift": _drift(contribution),
            "note": (
                "Not enough cleared history in the last "
                f"{months} months to measure a trend."
            ),
        }

    suggestion = solve_for_contribution(contribution, trend, today=today)
    return {
        "contribution_id": contribution.id,
        "account_id": contribution.account_id,
        "trend": trend,
        "suggestion": suggestion,
        "drift": _drift(contribution),
        "note": None,
    }


def _drift(contribution: Contribution) -> Decimal | None:
    """How far the planned per-paycheck figure is from what is actually scheduled.

    None when no reminder is linked, because there is nothing to compare against
    — which is different from a drift of zero.
    """
    if not contribution.reminder_id:
        return None
    scheduled = contribution.reminder.amount or Decimal("0")
    return ((contribution.per_paycheck or Decimal("0")) - abs(scheduled)).quantize(
        Decimal("0.01")
    )


def net_per_paycheck(periods: int = 6, today: date | None = None) -> Decimal | None:
    """Average take-home per *pay period*, not per paycheck.

    A household can have several earners paid on the same day, so paychecks are
    grouped by date and summed before averaging — otherwise two earners look
    like half the income. Real data swings 1622-1997 per individual cheque, so a
    single recent period is not representative and several are averaged.

    Returns None when there is no paycheck history to average.
    """
    today = today or get_todays_date_timezone_adjusted()
    rows = (
        Transaction.objects.filter(
            paycheck__isnull=False, transaction_date__lte=today
        )
        .select_related("paycheck")
        .order_by("-transaction_date")[: periods * 6]
    )
    by_date: dict[date, Decimal] = {}
    for tx in rows:
        by_date.setdefault(tx.transaction_date, Decimal("0"))
        by_date[tx.transaction_date] += tx.paycheck.net or Decimal("0")
    if not by_date:
        return None
    recent = [by_date[d] for d in sorted(by_date, reverse=True)[:periods]]
    return (sum(recent) / Decimal(len(recent))).quantize(Decimal("0.01"))


def funding_account_id() -> int | None:
    """The account the contributions are paid out of.

    Taken as the one most contributions draw on rather than configured
    separately, because that is already recorded on every linked reminder.
    """
    counts: dict[int, int] = {}
    for c in Contribution.objects.filter(
        active=True, reminder__isnull=False
    ).select_related("reminder"):
        source = c.reminder.reminder_source_account_id
        if source:
            counts[source] = counts.get(source, 0) + 1
    if not counts:
        return None
    return max(counts.items(), key=lambda kv: kv[1])[0]


def bucket_reminder_ids() -> set[int]:
    """Reminders that move money into a planned bucket.

    These are the allocation itself, so they are never counted as a change in
    what there is to allocate — reducing one is the planner's output, not an
    input to it.
    """
    return {
        c.reminder_id
        for c in Contribution.objects.filter(active=True, reminder__isnull=False)
        if c.reminder_id
    }


def forward_reminder_change(
    horizon_months: int = 12,
    today: date | None = None,
) -> tuple[Decimal, list[dict]]:
    """How much capacity changes over the horizon because reminders start or end.

    Measured drift says what the funding account does *today*. It cannot know
    that childcare stops in December or that the reimbursement paying for it
    stops with it, and those are exactly the changes worth planning around.

    Each non-bucket reminder on the funding account is compared against itself:
    what it will actually contribute over the horizon, versus what it would
    contribute if it simply carried on. The difference is the change in
    capacity. A reminder with no end date and a start in the past nets to zero
    and never appears, so this reports only what genuinely shifts.

    Returns the annualised change and a per-reminder breakdown, because "you
    will have 260 a paycheck less from January" is only actionable if it also
    says which commitments caused it.
    """
    account_id = funding_account_id()
    if account_id is None:
        return Decimal("0"), []

    today = today or get_todays_date_timezone_adjusted()
    horizon_years = Decimal(horizon_months) / 12
    end_date = today + timedelta(days=int(DAYS_PER_YEAR * horizon_years))
    bucket_ids = bucket_reminder_ids()

    changes: list[dict] = []
    total = Decimal("0")
    for reminder in Reminder.objects.filter(
        Q(reminder_source_account_id=account_id)
        | Q(reminder_destination_account_id=account_id)
    ).select_related("repeat"):
        if reminder.id in bucket_ids:
            continue
        per_year = occurrences_per_year(reminder.repeat)
        if per_year is None:
            # A one-off has nothing to carry on doing, so it cannot represent a
            # change in the run rate.
            continue

        # Already over: it is in neither today's run rate nor the horizon, so it
        # represents no change at all.
        if reminder.end_date and reminder.end_date < today:
            continue

        amount = _reminder_signed_amount(reminder, account_id)
        delta = _horizon_change(reminder, amount, per_year, today, end_date)
        if delta == 0:
            continue
        changes.append(
            {
                "reminder_id": reminder.id,
                "description": reminder.description,
                "change_per_year": (delta / horizon_years).quantize(Decimal("0.01")),
                "ends": reminder.end_date,
                "starts": reminder.start_date,
            }
        )
        total += delta

    return (total / horizon_years).quantize(Decimal("0.01")), changes


def _reminder_signed_amount(reminder, account_id: int) -> Decimal:
    """A reminder's amount from the funding account's point of view.

    Transfers and expenses are stored negative and direction lives in the
    source/destination pair, so a transfer *into* this account has to have its
    sign flipped to read as the inflow it is.
    """
    amount = reminder.amount or Decimal("0")
    if reminder.reminder_destination_account_id == account_id:
        return abs(amount)
    return amount


def _horizon_change(
    reminder, amount: Decimal, per_year: Decimal, today: date, end_date: date
) -> Decimal:
    """How much a reminder's contribution over the horizon differs from its run rate.

    Both sides are prorated over the *same* number of days, which is the whole
    point: a reminder that is already running and never ends must come out at
    exactly zero. Measuring the horizon in occurrences but the run rate in years
    left a few days' rounding on every one of them, and twenty untouched
    reminders summed that noise into a 250-a-paycheck capacity change that
    nothing had actually caused.

    Occurrences are prorated rather than enumerated — the exact dates do not
    matter to a rate, and walking a biweekly series over a year to count 26 of
    them is a lot of work to arrive at 26.

    "Already running" cannot be read from `start_date`, which this app rolls
    forward in step with `next_date` and so is always in the future. It is taken
    instead from the next occurrence falling within a couple of periods: a
    monthly bill due next month is running, one whose first payment is six
    months out is a new commitment that today's rate knows nothing about.
    """
    horizon_days = Decimal((end_date - today).days)
    if horizon_days <= 0 or per_year <= 0:
        return Decimal("0.00")

    period_days = DAYS_PER_YEAR / per_year
    next_date = reminder.next_date or reminder.start_date or today
    # Two periods of slack, not one: a monthly reminder whose current occurrence
    # has already been generated legitimately sits over a month out.
    running = Decimal((next_date - today).days) <= period_days * 2

    first = today if running else next_date
    last = end_date
    if reminder.end_date and reminder.end_date < last:
        last = reminder.end_date
    active_days = Decimal(max(0, (last - first).days))

    # What it will really contribute, versus what today's rate implies. A
    # commitment that has not begun contributes nothing to today's rate, so its
    # whole horizon effect is a change.
    actual = amount * per_year * (active_days / DAYS_PER_YEAR)
    steady = (
        amount * per_year * (horizon_days / DAYS_PER_YEAR)
        if running
        else Decimal("0")
    )
    return (actual - steady).quantize(Decimal("0.01"))


def allocatable_per_paycheck(
    current_total: Decimal,
    months: int = 6,
    today: date | None = None,
) -> tuple[Decimal | None, Decimal | None]:
    """How much there is to allocate each paycheck, and how the account drifted.

    NOT take-home pay. The funding account is a hub, not a wallet: money leaves
    it for the buckets and comes back from them to pay the bills those buckets
    exist for. Over six months of real data it saw 7,893 a paycheck in and
    7,915 out against a take-home of 3,556 — so measuring capacity against
    take-home ignores the ~786 a paycheck of bills that leave it directly and
    never pass through a bucket.

    The definition that works falls out of "every dollar should be working
    somewhere", which means the funding account should net to zero:

        allocatable = what is allocated today + however much it actually drifted

    If it held steady, today's allocation is exactly what there is. If it grew,
    that surplus could be put to work; if it shrank, the allocation is already
    beyond its means.
    """
    account_id = funding_account_id()
    if account_id is None:
        return None, None

    today = today or get_todays_date_timezone_adjusted()
    start_date = today - timedelta(days=int(DAYS_PER_MONTH) * months)
    try:
        cleared = TransactionStatus.objects.get(slug="cleared")
    except TransactionStatus.DoesNotExist:
        return None, None

    account_q = Q(source_account_id=account_id) | Q(
        destination_account_id=account_id
    )
    net_change = Decimal("0")
    for tx in Transaction.objects.filter(
        account_q,
        status=cleared,
        transaction_date__gte=start_date,
        transaction_date__lte=today,
    ).select_related("transaction_type"):
        net_change += _signed_amount(tx, account_id)

    window_days = Decimal((today - start_date).days or 1)
    paychecks_in_window = window_days / DAYS_PER_YEAR * Decimal("26.0893")
    if paychecks_in_window <= 0:
        return None, None
    drift = (net_change / paychecks_in_window).quantize(Decimal("0.01"))
    return (current_total + drift).quantize(Decimal("0.01")), drift


def minimum_per_paycheck(trend: Trend | None) -> Decimal:
    """The non-negotiable share: what dated obligations demand over the horizon.

    Only *scheduled* outflows count — the mortgage, the tax bill, the insurance
    premium. Ad-hoc spending is real but it is not dated, so it can be squeezed;
    a quarterly property-tax payment cannot. The account's existing balance is
    spent first, because money already in the bucket does not need contributing
    twice.

    Buckets whose spending is entirely ad-hoc (groceries, gifts) return zero
    here. That is not a claim they need nothing — it is a claim that nothing
    about them is *fixed*, which is exactly what the tier is for.
    """
    if trend is None or trend.paychecks_in_horizon <= 0:
        return Decimal("0.00")
    obligations = trend.scheduled_flow_per_month * Decimal(trend.horizon_months)
    if obligations >= 0:
        return Decimal("0.00")
    shortfall = -obligations - trend.current_balance
    if shortfall <= 0:
        return Decimal("0.00")
    return (shortfall / trend.paychecks_in_horizon).quantize(Decimal("0.01"))


def paycheck_headroom(
    current_total: Decimal,
    suggested_total: Decimal,
    income_adjustment: Decimal = Decimal("0"),
    months: int = 6,
    horizon_months: int = 12,
    today: date | None = None,
) -> dict:
    """What there is to allocate, and how it compares with what is wanted.

    `current_total` must be the *effective* allocation — scheduled transfers
    plus the top-ups being made by hand. Passing the scheduled figure alone
    understates the baseline by everything that is already being contributed
    off-plan, which on real data was 694 a paycheck and produced a shortfall
    that the account balances flatly contradicted.

    Capacity is built from three terms:

    - what is being allocated today, which is the only measurement of what the
      household can actually sustain;
    - how the funding account drifted while doing it, so an allocation beyond
      its means shows up as a negative;
    - how much the reminders say that changes over the horizon, which is the
      only part drift cannot see.

    `income_adjustment` is supplied rather than inferred. A raise is a future
    event, and with more than one earner the per-cheque noise is far larger than
    a typical raise, so there is nothing in history to detect it from.
    """
    allocatable, drift = allocatable_per_paycheck(
        current_total, months=months, today=today
    )
    take_home = net_per_paycheck(today=today)
    if allocatable is None:
        return {
            "net_per_paycheck": take_home,
            "allocatable_per_paycheck": None,
            "funding_account_drift": None,
            "forward_reminder_change": None,
            "reminder_changes": [],
            "income_adjustment": income_adjustment,
            "headroom_now": None,
            "headroom_if_applied": None,
            "affordable": None,
            "note": (
                "No linked reminders, so there is no funding account to measure "
                "against."
            ),
        }
    forward_change, changes = forward_reminder_change(
        horizon_months=horizon_months, today=today
    )
    # Expressed per paycheck to match everything else on this page. The change
    # is annual, so it divides by the pay cadence rather than the horizon.
    forward_per_paycheck = (forward_change / Decimal("26.0893")).quantize(
        Decimal("0.01")
    )
    adjusted = allocatable + income_adjustment + forward_per_paycheck
    return {
        "net_per_paycheck": take_home,
        "allocatable_per_paycheck": adjusted,
        "funding_account_drift": drift,
        "forward_reminder_change": forward_per_paycheck,
        "reminder_changes": changes,
        "income_adjustment": income_adjustment,
        "headroom_now": (adjusted - current_total).quantize(Decimal("0.01")),
        "headroom_if_applied": (adjusted - suggested_total).quantize(
            Decimal("0.01")
        ),
        "affordable": adjusted >= suggested_total,
        "note": None,
    }


def allocate_capacity(rows: list, capacity: Decimal | None) -> dict:
    """Distribute a fixed pot across the contributions, instead of summing wishes.

    Solving each bucket alone and adding the answers up asks "what would make
    every account healthy", which is a different question from "what should I do
    with the money I have". On real data the first question returned 3,666 a
    paycheck against 2,820 scheduled and called the difference a shortfall,
    while the accounts themselves were net *ahead* — because 694 a paycheck of
    hand top-ups were funding the gap and no one had counted them.

    So the pot is distributed in tiers:

    1. **Obligations** — dated, unavoidable, funded first and in full.
    2. **Goals** — what each bucket asked for above its obligations, rationed
       pro-rata when there is not enough to satisfy everything.
    3. **Whatever is left** — split across the `maximise` buckets, which exist
       precisely to absorb it.

    Each row is compared against its *effective* funding, so the result reads as
    a reallocation rather than a demand for new money.

    `rows` are PlannerRowOut-shaped: anything carrying `.suggestion`,
    `.current_per_paycheck` and `.topup_per_paycheck`. Kept structural rather
    than typed so the service never imports the API schema.
    """
    planned = [r for r in rows if r.suggestion is not None]
    if capacity is None or not planned:
        return {
            "capacity_per_paycheck": capacity,
            "obligations_total": Decimal("0.00"),
            "desired_total": Decimal("0.00"),
            "allocated_total": Decimal("0.00"),
            "effective_total": Decimal("0.00"),
            "unallocated": Decimal("0.00"),
            "net_change_total": Decimal("0.00"),
            "feasible": None,
            "shortfall": None,
            "moves": [],
            "note": (
                "No capacity figure, so there is nothing to distribute."
                if capacity is None
                else "No contributions with goals to allocate between."
            ),
        }

    maximise = [
        r for r in planned if r.suggestion.goal_type == Contribution.GOAL_MAXIMISE
    ]
    fixed = [
        r for r in planned if r.suggestion.goal_type != Contribution.GOAL_MAXIMISE
    ]

    obligations = sum((r.minimum_per_paycheck for r in fixed), Decimal("0"))
    desired = sum((r.suggestion.required_per_paycheck for r in fixed), Decimal("0"))
    effective_total = sum(
        (r.effective_per_paycheck for r in planned), Decimal("0")
    )

    feasible = capacity >= obligations
    if not feasible:
        # Obligations alone overrun the pot. Nothing discretionary can be funded,
        # and pretending otherwise would bury the one fact that matters.
        share = capacity / obligations if obligations > 0 else Decimal("0")
        for row in fixed:
            row.allocated_per_paycheck = (
                row.minimum_per_paycheck * share
            ).quantize(Decimal("0.01"))
        for row in maximise:
            row.allocated_per_paycheck = Decimal("0.00")
        allocated_total = sum(
            (r.allocated_per_paycheck for r in planned), Decimal("0")
        )
        return {
            "capacity_per_paycheck": capacity,
            "obligations_total": obligations.quantize(Decimal("0.01")),
            "desired_total": desired.quantize(Decimal("0.01")),
            "allocated_total": allocated_total.quantize(Decimal("0.01")),
            "effective_total": effective_total.quantize(Decimal("0.01")),
            "unallocated": Decimal("0.00"),
            "net_change_total": (
                allocated_total - effective_total
            ).quantize(Decimal("0.01")),
            "feasible": False,
            "shortfall": (obligations - capacity).quantize(Decimal("0.01")),
            "moves": _moves_from(planned),
            "note": (
                "Dated obligations alone exceed what there is to allocate. This "
                "is not a budgeting problem the planner can solve by moving "
                "money between buckets."
            ),
        }

    # Tier 2: ration what is left across the gap between obligation and goal.
    remaining = capacity - obligations
    wants = sum(
        (
            max(Decimal("0"), r.suggestion.required_per_paycheck - r.minimum_per_paycheck)
            for r in fixed
        ),
        Decimal("0"),
    )
    if wants <= 0:
        ratio = Decimal("0")
    elif remaining >= wants:
        ratio = Decimal("1")
    else:
        ratio = remaining / wants

    for row in fixed:
        want = max(
            Decimal("0"),
            row.suggestion.required_per_paycheck - row.minimum_per_paycheck,
        )
        row.allocated_per_paycheck = (
            row.minimum_per_paycheck + want * ratio
        ).quantize(Decimal("0.01"))

    # Tier 3: the residual is what "maximise" means.
    leftover = remaining - (wants * ratio)
    if leftover < 0:
        leftover = Decimal("0")
    if maximise:
        share = (leftover / Decimal(len(maximise))).quantize(Decimal("0.01"))
        for row in maximise:
            row.allocated_per_paycheck = share
            row.suggestion.required_per_paycheck = share
            row.suggestion.delta_per_paycheck = (
                share - row.suggestion.current_per_paycheck
            ).quantize(Decimal("0.01"))
            row.suggestion.reason = (
                f"{share} a paycheck left once obligations and goals are funded."
                if share > 0
                else "Nothing left once obligations and goals are funded."
            )
            if share == 0:
                row.suggestion.warning = (
                    "The other goals already claim everything there is to "
                    "allocate — nothing left to put here."
                )
        unallocated = Decimal("0.00")
    else:
        unallocated = leftover.quantize(Decimal("0.01"))

    allocated_total = sum((r.allocated_per_paycheck for r in planned), Decimal("0"))
    return {
        "capacity_per_paycheck": capacity,
        "obligations_total": obligations.quantize(Decimal("0.01")),
        "desired_total": desired.quantize(Decimal("0.01")),
        "allocated_total": allocated_total.quantize(Decimal("0.01")),
        "effective_total": effective_total.quantize(Decimal("0.01")),
        "unallocated": unallocated,
        # Negative when the plan has to shrink overall, which the paired moves
        # cannot show: they only ever match a giver to a taker, so an
        # across-the-board reduction leaves givers unpaired and silently
        # unexplained.
        "net_change_total": (allocated_total - effective_total).quantize(
            Decimal("0.01")
        ),
        "feasible": True,
        "shortfall": Decimal("0.00"),
        "moves": _moves_from(planned),
        "note": (
            None
            if ratio >= 1
            else (
                "Not enough to meet every goal in full, so what is left after "
                "obligations is shared out in proportion to what each asked for."
            )
        ),
    }


def _moves_from(rows: list) -> list[dict]:
    """Pair the buckets giving money up with the ones taking it on.

    "Move 122 from Reno to Ellie" is the sentence someone can act on; "Reno
    -122, Ellie +247" is a table they have to solve themselves. Sources are
    drained largest-first into destinations largest-first, which keeps the
    number of transfers down — the point is to be actionable, and six moves
    beat sixteen.
    """
    givers = []
    takers = []
    for row in rows:
        delta = (
            row.allocated_per_paycheck - row.effective_per_paycheck
        ).quantize(Decimal("0.01"))
        row.move_per_paycheck = delta
        if delta < 0:
            givers.append([row, -delta])
        elif delta > 0:
            takers.append([row, delta])

    givers.sort(key=lambda pair: pair[1], reverse=True)
    takers.sort(key=lambda pair: pair[1], reverse=True)

    moves: list[dict] = []
    i = j = 0
    while i < len(givers) and j < len(takers):
        giver, available = givers[i]
        taker, needed = takers[j]
        amount = min(available, needed)
        if amount > 0:
            moves.append(
                {
                    "from_contribution_id": giver.contribution_id,
                    "from_contribution": giver.contribution,
                    "to_contribution_id": taker.contribution_id,
                    "to_contribution": taker.contribution,
                    "amount_per_paycheck": amount.quantize(Decimal("0.01")),
                }
            )
        givers[i][1] -= amount
        takers[j][1] -= amount
        if givers[i][1] <= 0:
            i += 1
        if takers[j][1] <= 0:
            j += 1
    return moves
