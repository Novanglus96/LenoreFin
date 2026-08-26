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
from transactions.models import Transaction, TransactionStatus
from utils.dates import get_todays_date_timezone_adjusted

# Average days per month/year, so a cadence in months and one in weeks are
# comparable without pretending every month is 30 days.
DAYS_PER_MONTH = Decimal("30.4375")
DAYS_PER_YEAR = Decimal("365.25")

# Below this many cleared transactions a trend is noise, not signal.
MIN_DATA_POINTS = 3


@dataclass
class Trend:
    """What an account does when nobody is topping it up."""

    natural_flow_per_month: Decimal
    observed_slope_per_month: Decimal
    r_squared: float
    data_points: int
    window_months: int
    current_balance: Decimal
    excluded_contribution_total: Decimal


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


def _is_contribution_transfer(tx, account_id: int, source_account_id: int | None) -> bool:
    """True when this transaction is the contribution topping the account up.

    Real transactions carry no link back to the reminder that spawned them, so
    the contribution is identified by its shape instead: a transfer landing in
    this account. When the contribution has a linked reminder we can be strict
    and require the money to have come from that reminder's source account;
    without one, any incoming transfer is treated as a top-up, which is the
    right default for a savings account funded from checking.
    """
    if not tx.transaction_type or tx.transaction_type.slug != "transfer":
        return False
    if tx.destination_account_id != account_id:
        return False
    if source_account_id is not None:
        return tx.source_account_id == source_account_id
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


def analyze_account_trend(
    account_id: int,
    months: int = 6,
    source_account_id: int | None = None,
    today: date | None = None,
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

    # Walk the window once, accumulating the real balance curve while keeping
    # the contribution's own top-ups in a separate bucket.
    natural_flow = Decimal("0")
    contributed = Decimal("0")
    balance = balance_at_start
    points: list[tuple[float, float]] = []
    for tx in window:
        amount = _signed_amount(tx, account_id)
        balance += amount
        if _is_contribution_transfer(tx, account_id, source_account_id):
            contributed += amount
        else:
            natural_flow += amount
        points.append(((tx.transaction_date - start_date).days, float(balance)))

    slope_per_day, r_squared = _linear_regression(points)
    window_days = Decimal((today - start_date).days or 1)
    months_elapsed = window_days / DAYS_PER_MONTH

    return Trend(
        natural_flow_per_month=(natural_flow / months_elapsed).quantize(
            Decimal("0.01")
        ),
        observed_slope_per_month=(
            Decimal(str(slope_per_day)) * DAYS_PER_MONTH
        ).quantize(Decimal("0.01")),
        r_squared=round(r_squared, 4),
        data_points=len(window),
        window_months=months,
        current_balance=balance.quantize(Decimal("0.01")),
        excluded_contribution_total=contributed.quantize(Decimal("0.01")),
    )


def paychecks_per_year(contribution: Contribution) -> Decimal:
    """How many times a year this contribution is paid.

    Derived from the linked reminder's repeat rather than a global payday
    setting, so two contributions on different cadences each solve correctly.
    Falls back to biweekly, which is the overwhelmingly common case and the
    only sane guess when nothing is linked.
    """
    biweekly = Decimal("26")
    reminder = contribution.reminder
    if not reminder or not reminder.repeat:
        return biweekly
    repeat = reminder.repeat
    period_days = (
        Decimal(repeat.days or 0)
        + Decimal(repeat.weeks or 0) * 7
        + Decimal(repeat.months or 0) * DAYS_PER_MONTH
        + Decimal(repeat.years or 0) * DAYS_PER_YEAR
    )
    if period_days <= 0:
        return biweekly
    # Quantized because the raw division is unbounded (365.25/14 runs to 27
    # decimal places) and this value is serialised as well as multiplied.
    # Four places is far finer than any cadence distinction that matters.
    return (DAYS_PER_YEAR / period_days).quantize(Decimal("0.0001"))


def _per_paycheck(monthly: Decimal, per_year: Decimal) -> Decimal:
    """Convert a monthly figure to a per-paycheck one at this cadence."""
    if per_year <= 0:
        return Decimal("0")
    return (monthly * 12) / per_year


def solve_for_contribution(
    contribution: Contribution,
    trend: Trend,
    today: date | None = None,
) -> Suggestion | None:
    """Turn a goal plus a measured trend into a required per-paycheck figure.

    Returns None for a contribution with no goal — there is nothing to solve.
    """
    goal = contribution.goal_type
    if goal == Contribution.GOAL_NONE:
        return None

    today = today or get_todays_date_timezone_adjusted()
    per_year = paychecks_per_year(contribution)
    current = contribution.per_paycheck or Decimal("0")

    # The account's own drift, expressed in the same units as a contribution.
    natural = _per_paycheck(trend.natural_flow_per_month, per_year)

    warning = None
    achievable = True

    if goal == Contribution.GOAL_HOLD:
        # Offset the drift exactly: contribution + natural == 0.
        required = -natural
        reason = (
            f"Spending runs {trend.natural_flow_per_month}/month against this "
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
            f"Offsetting {trend.natural_flow_per_month}/month of drift and "
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
        # The floor binds at the account's low point, which for a steadily
        # draining account is the end of the horizon. Solve so the balance
        # never crosses the floor over the next year.
        horizon_paychecks = per_year
        projected = trend.current_balance + (natural + current) * horizon_paychecks
        if projected >= contribution.goal_amount:
            required = current
            reason = (
                f"Projected to sit at {projected.quantize(Decimal('0.01'))} in a "
                f"year, above the {contribution.goal_amount} floor."
            )
        else:
            shortfall = contribution.goal_amount - projected
            required = current + (shortfall / horizon_paychecks)
            reason = (
                f"Projected to fall to {projected.quantize(Decimal('0.01'))} in a "
                f"year, {shortfall.quantize(Decimal('0.01'))} below the floor."
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
    monthly_natural = trend.natural_flow_per_month
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
    )
    if trend is None:
        return {
            "contribution_id": contribution.id,
            "account_id": contribution.account_id,
            "trend": None,
            "suggestion": None,
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
