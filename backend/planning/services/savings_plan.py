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

4. `capacity` — the same arithmetic applied to the funding account, giving the
   largest total that can be allocated without pushing it below its buffer at
   any point in the year. A scalar, but derived from the whole path, so a plan
   that balances over twelve months while overdrawing in September is rejected
   rather than averaged away.

5. `build_plan` — fund every minimum, then fill goals in priority order until
   the money runs out, then sweep the remainder.

6. `_verify` — re-check the finished plan against every path. It should pass by
   construction; it has caught enough arithmetic slips to be worth keeping.

The whole thing costs one forecast pass per account. Candidate allocations are
evaluated by superposition rather than by re-running the forecast, which is
exact for a fixed transfer and turns a ~1.6s simulation into arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Q

from accounts.models import Account
from planning.models import Contribution
from planning.services.planner import (
    DAYS_PER_MONTH,
    DAYS_PER_YEAR,
    analyze_account_trend,
    funding_account_id,
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


@dataclass
class PathPoint:
    day: int
    when: date
    balance: Decimal


@dataclass
class AccountPlan:
    """One contribution's share of the plan, and the evidence behind it."""

    contribution_id: int
    contribution: str
    account_id: int | None
    account_name: str | None
    priority: int
    sweep: bool
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


@dataclass
class PlanResult:
    generated_for: date
    horizon_months: int
    buffer: Decimal
    paychecks: list[date]
    paychecks_in_horizon: int

    capacity_per_paycheck: Decimal
    minimums_total: Decimal
    targets_total: Decimal
    planned_total: Decimal
    current_total: Decimal
    unallocated: Decimal

    feasible: bool
    verified: bool
    lines: list[AccountPlan] = field(default_factory=list)
    breaches: list[dict] = field(default_factory=list)
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


def budget_events(
    budget, today: date, end_date: date
) -> list[tuple[date, Decimal]]:
    """When a budget's spending actually lands, and how much.

    Dated events rather than a smooth rate, because when the money is needed
    decides how much has to be saved by then. Christmas is the case that proves
    it: 1,995 a year trickled evenly never requires the account to hold more
    than a couple of hundred, while the same 1,995 landing in December means the
    bucket must have the whole sum by then. The second is what actually happens.
    """
    repeat = budget.repeat
    if repeat is None or not budget.amount:
        return []
    period = (
        Decimal(repeat.days or 0)
        + Decimal(repeat.weeks or 0) * 7
        + Decimal(repeat.months or 0) * DAYS_PER_MONTH
        + Decimal(repeat.years or 0) * DAYS_PER_YEAR
    )
    if period <= 0:
        return []

    step = int(period)
    cursor = budget.next_start or budget.start_day or today
    # A budget whose cycle started before today is already part way through; the
    # remainder of the current cycle still has to be funded.
    while cursor < today:
        cursor = cursor + timedelta(days=step)

    events: list[tuple[date, Decimal]] = []
    guard = 0
    while cursor <= end_date and guard < 400:
        events.append((cursor, -abs(budget.amount)))
        cursor = cursor + timedelta(days=step)
        guard += 1
    return events


def budget_per_paycheck(budget) -> Decimal:
    """A budget's amount expressed in the cadence the planner allocates in."""
    repeat = budget.repeat
    if repeat is None or not budget.amount:
        return Decimal("0.00")
    period = (
        Decimal(repeat.days or 0)
        + Decimal(repeat.weeks or 0) * 7
        + Decimal(repeat.months or 0) * DAYS_PER_MONTH
        + Decimal(repeat.years or 0) * DAYS_PER_YEAR
    )
    if period <= 0:
        return Decimal("0.00")
    per_year = DAYS_PER_YEAR / period
    return (abs(budget.amount) * per_year / Decimal("26.0893")).quantize(
        Decimal("0.01")
    )


def baseline_path(
    account_id: int,
    today: date,
    end_date: date,
    exclude_descriptions: set[str],
    spend_events: list[tuple[date, Decimal]] | None = None,
    replace_adhoc_reimbursements_to: int | None = None,
) -> tuple[list[PathPoint], Decimal]:
    """An account's projected balance with named flows removed and budgets added.

    `exclude_descriptions` takes out the transfers the plan is deciding, so the
    plan is superimposed on an account nobody is funding yet. Their deltas are
    backed out of the running balance rather than merely skipped, otherwise
    every later point still carries them.

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
        rows, opening = get_account_transactions_and_balances(
            end_date, account_id, False, True, today, False
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
        description = _field(row, "description")
        # Excluded flows contribute no delta, but the date is still a point on
        # the path. Skipping them outright made the path collapse to one entry
        # for any bucket whose only modelled flow is the contribution being
        # planned, and a one-point path can never show drift accumulating.
        keep = description not in exclude_descriptions
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

    path: list[PathPoint] = []
    for day, when, delta in steps:
        running += delta
        path.append(
            PathPoint(day=day, when=when, balance=running.quantize(Decimal("0.01")))
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
        needed.quantize(Decimal("0.01")),
        low.quantize(Decimal("0.01")),
        low_date,
        warning,
    )


def capacity_per_paycheck(
    path: list[PathPoint],
    buffer: Decimal,
    paycheck_days: list[int],
) -> tuple[Decimal, list[dict]]:
    """The largest total per paycheck the funding account can sustain all year.

    The mirror of `required_rate`: every point demands
    `total <= (baseline(t) - buffer) / paychecks_so_far(t)`, and capacity is
    whichever point allows least. Deriving it from the path rather than from an
    annual average is the point — this account opens at 653.45 and bottoms at
    393.73 within a week, so the near term binds far harder than the year does.

    A point that breaches the buffer before any paycheck lands cannot be fixed
    by allocating less, so it is reported separately rather than driving
    capacity negative.
    """
    allowed = None
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
        limit = headroom / landed
        if allowed is None or limit < allowed:
            allowed = limit

    if allowed is None:
        allowed = Decimal("0")
    if allowed < 0:
        allowed = Decimal("0")
    return allowed.quantize(Decimal("0.01")), blocked


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
    return (gap / landed).quantize(Decimal("0.01"))


def build_plan(
    horizon_months: int = 12,
    window_months: int = 6,
    buffer: Decimal | None = None,
    today: date | None = None,
) -> PlanResult:
    """Produce a savings plan that provably works, or explain why none does."""
    from utils.dates import get_todays_date_timezone_adjusted

    today = today or get_todays_date_timezone_adjusted()
    buffer = DEFAULT_BUFFER if buffer is None else buffer
    end_date = today + timedelta(days=int(DAYS_PER_YEAR * horizon_months / 12))

    fund_id = funding_account_id()
    contributions = list(
        Contribution.objects.filter(active=True)
        .select_related("account", "reminder", "reminder__repeat")
        .order_by("priority", "id")
    )
    notes: list[str] = []

    if fund_id is None:
        return PlanResult(
            generated_for=today,
            horizon_months=horizon_months,
            buffer=buffer,
            paychecks=[],
            paychecks_in_horizon=0,
            capacity_per_paycheck=Decimal("0"),
            minimums_total=Decimal("0"),
            targets_total=Decimal("0"),
            planned_total=Decimal("0"),
            current_total=Decimal("0"),
            unallocated=Decimal("0"),
            feasible=False,
            verified=False,
            notes=[
                "No contribution has a linked reminder, so there is no funding "
                "account to plan against."
            ],
        )

    paychecks = pay_calendar(today, end_date, fund_id)
    if not paychecks:
        return PlanResult(
            generated_for=today,
            horizon_months=horizon_months,
            buffer=buffer,
            paychecks=[],
            paychecks_in_horizon=0,
            capacity_per_paycheck=Decimal("0"),
            minimums_total=Decimal("0"),
            targets_total=Decimal("0"),
            planned_total=Decimal("0"),
            current_total=Decimal("0"),
            unallocated=Decimal("0"),
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
    plan_descriptions = {
        c.reminder.description
        for c in contributions
        if c.reminder_id and c.reminder.description
    }

    fund_path, _ = baseline_path(fund_id, today, end_date, plan_descriptions)
    capacity, blocked = capacity_per_paycheck(fund_path, buffer, paycheck_days)

    lines: list[AccountPlan] = []
    for contribution in contributions:
        lines.append(
            _line_for(
                contribution,
                today,
                end_date,
                paycheck_days,
                window_months,
                horizon_months,
            )
        )

    minimums_total = sum((line.minimum_per_paycheck for line in lines), Decimal("0"))
    targets_total = sum((line.target_per_paycheck for line in lines), Decimal("0"))
    current_total = sum((line.current_per_paycheck for line in lines), Decimal("0"))

    if blocked:
        notes.append(
            f"The funding account drops below the {buffer} buffer on "
            f"{blocked[0]['when']} before any paycheck lands. No allocation can "
            f"fix that — it needs {blocked[0]['short_by']} put in now."
        )

    feasible = minimums_total <= capacity
    if not feasible:
        levers = _levers(lines, minimums_total - capacity, capacity)
        for line in lines:
            line.planned_per_paycheck = Decimal("0.00")
        return PlanResult(
            generated_for=today,
            horizon_months=horizon_months,
            buffer=buffer,
            paychecks=paychecks,
            paychecks_in_horizon=len(paychecks),
            capacity_per_paycheck=capacity,
            minimums_total=minimums_total.quantize(Decimal("0.01")),
            targets_total=targets_total.quantize(Decimal("0.01")),
            planned_total=Decimal("0.00"),
            current_total=current_total.quantize(Decimal("0.01")),
            unallocated=Decimal("0.00"),
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
        give = min(want, remaining)
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
    if remaining > 0 and sweeps:
        share = (remaining / Decimal(len(sweeps))).quantize(Decimal("0.01"))
        for line in sweeps:
            line.planned_per_paycheck = (
                line.planned_per_paycheck + share
            ).quantize(Decimal("0.01"))
            line.reason = f"{share} a paycheck left over once everything else is funded."
        remaining = Decimal("0")

    planned_total = sum((line.planned_per_paycheck for line in lines), Decimal("0"))
    breaches = _verify(
        lines, fund_path, paycheck_days, buffer, today, end_date, plan_descriptions
    )
    if remaining > 0:
        notes.append(
            f"{remaining.quantize(Decimal('0.01'))} a paycheck is left unallocated "
            "— every goal is fully funded and no account is set to absorb the rest."
        )

    return PlanResult(
        generated_for=today,
        horizon_months=horizon_months,
        buffer=buffer,
        paychecks=paychecks,
        paychecks_in_horizon=len(paychecks),
        capacity_per_paycheck=capacity,
        minimums_total=minimums_total.quantize(Decimal("0.01")),
        targets_total=targets_total.quantize(Decimal("0.01")),
        planned_total=planned_total.quantize(Decimal("0.01")),
        current_total=current_total.quantize(Decimal("0.01")),
        unallocated=remaining.quantize(Decimal("0.01")),
        feasible=True,
        verified=not breaches,
        lines=lines,
        breaches=breaches,
        notes=notes,
    )


def _line_for(
    contribution: Contribution,
    today: date,
    end_date: date,
    paycheck_days: list[int],
    window_months: int,
    horizon_months: int,
) -> AccountPlan:
    """Work out one contribution's minimum and target from its own account.

    Three inputs, in order of authority: the budgets it funds (what you plan to
    spend), the dated reminders on its account (what you are committed to), and
    the target balance (what you want it to build up to). Measured behaviour is
    reported but never planned on — that is the whole point of the budgets.
    """
    per_year = paychecks_per_year(contribution)
    current = contribution.per_paycheck or Decimal("0")
    stated_minimum = contribution.minimum_per_paycheck
    own = (
        contribution.reminder.description
        if contribution.reminder_id and contribution.reminder.description
        else None
    )

    budgets = list(contribution.budgets.select_related("repeat").all())
    budgeted = sum(
        (budget_per_paycheck(b) for b in budgets), Decimal("0")
    ).quantize(Decimal("0.01"))
    budget_names = [b.name for b in budgets]

    if not contribution.account_id:
        minimum = stated_minimum if stated_minimum is not None else Decimal("0.00")
        return AccountPlan(
            contribution_id=contribution.id,
            contribution=contribution.contribution,
            account_id=None,
            account_name=None,
            priority=contribution.priority,
            sweep=contribution.sweep,
            paychecks_per_year=per_year,
            current_per_paycheck=current,
            minimum_per_paycheck=minimum,
            minimum_is_stated=stated_minimum is not None,
            target_per_paycheck=minimum,
            planned_per_paycheck=Decimal("0.00"),
            budgeted_per_paycheck=budgeted,
            budget_names=budget_names,
            target_balance=contribution.target_balance,
            projected_low=Decimal("0.00"),
            projected_low_date=None,
            observed_spend_per_month=Decimal("0.00"),
            spend_variance_per_paycheck=Decimal("0.00"),
            reason="No account linked, so there is nothing to project.",
            warning="Link an account to include this in the plan.",
        )

    spend_events: list[tuple[date, Decimal]] = []
    for budget in budgets:
        spend_events.extend(budget_events(budget, today, end_date))

    path, _ = baseline_path(
        contribution.account_id,
        today,
        end_date,
        {own} if own else set(),
        spend_events=spend_events,
        # Only when budgets are supplying the spending; otherwise the recorded
        # reimbursements are the only evidence there is.
        replace_adhoc_reimbursements_to=(
            contribution.reminder.reminder_source_account_id
            if budgets and contribution.reminder_id
            else None
        ),
    )

    # Solvency, nothing more: this account must not go overdrawn once its
    # budgets and its dated obligations are both on the path. Whatever buffer it
    # would *like* to hold is a target competing for the remainder rather than
    # outranking someone else's mortgage.
    derived, low, low_date, warning = required_rate(
        path, Decimal("0"), paycheck_days
    )
    minimum = max(derived, stated_minimum or Decimal("0"))

    if contribution.sweep:
        target = minimum
        reason = "Takes whatever is left once everything else is funded."
    elif contribution.target_balance is not None:
        needed = rate_to_reach(
            path, contribution.target_balance, contribution.target_date, today,
            paycheck_days,
        )
        target = max(minimum, needed)
        reason = (
            f"Building to {contribution.target_balance}"
            + (f" by {contribution.target_date}" if contribution.target_date else "")
            + "."
        )
    elif budgets:
        target = minimum
        reason = "Covering " + ", ".join(budget_names) + "."
    else:
        target = minimum
        reason = "Covering its dated obligations."

    # Measured behaviour, reported as a cross-check. A budget that disagrees
    # sharply with what the account actually spends is worth knowing about, but
    # it is the budget the plan is built on.
    trend = analyze_account_trend(
        contribution.account_id,
        months=window_months,
        source_account_id=(
            contribution.reminder.reminder_source_account_id
            if contribution.reminder_id
            else None
        ),
        today=today,
        contribution_description=own,
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
    if budgets and variance < -Decimal("25"):
        note = (
            f"Budgeted {budgeted} a paycheck, but this account has actually been "
            f"spending {abs(observed_per_paycheck)}. The plan follows the budget."
        )
        warning = f"{warning} {note}" if warning else note

    return AccountPlan(
        contribution_id=contribution.id,
        contribution=contribution.contribution,
        account_id=contribution.account_id,
        account_name=contribution.account.account_name,
        priority=contribution.priority,
        sweep=contribution.sweep,
        paychecks_per_year=per_year,
        current_per_paycheck=current,
        minimum_per_paycheck=minimum,
        minimum_is_stated=stated_minimum is not None,
        target_per_paycheck=target,
        planned_per_paycheck=Decimal("0.00"),
        budgeted_per_paycheck=budgeted,
        budget_names=budget_names,
        target_balance=contribution.target_balance,
        projected_low=low,
        projected_low_date=low_date,
        observed_spend_per_month=observed,
        spend_variance_per_paycheck=variance,
        reason=reason,
        warning=warning,
    )


def _verify(
    lines: list[AccountPlan],
    fund_path: list[PathPoint],
    paycheck_days: list[int],
    buffer: Decimal,
    today: date,
    end_date: date,
    plan_descriptions: set[str],
) -> list[dict]:
    """Re-check the finished plan against every path it claims to satisfy.

    Superposition should make this redundant — the rates were derived from these
    very paths — but "should" is doing a lot of work in a module that decides
    where someone's money goes, and this has caught real arithmetic slips.
    """
    breaches: list[dict] = []

    total = sum((line.planned_per_paycheck for line in lines), Decimal("0"))
    for point in fund_path:
        landed = Decimal(_paychecks_before(point.day, paycheck_days))
        balance = point.balance - total * landed
        if balance < buffer:
            breaches.append(
                {
                    "account": "funding",
                    "account_name": None,
                    "when": point.when,
                    "balance": balance.quantize(Decimal("0.01")),
                    "floor": buffer,
                }
            )
            break

    for line in lines:
        if not line.account_id:
            continue
        contribution = Contribution.objects.filter(pk=line.contribution_id).first()
        spend_events: list[tuple[date, Decimal]] = []
        if contribution:
            for budget in contribution.budgets.select_related("repeat").all():
                spend_events.extend(budget_events(budget, today, end_date))
        path, _ = baseline_path(
            line.account_id,
            today,
            end_date,
            plan_descriptions,
            spend_events=spend_events,
        )
        for point in path:
            landed = Decimal(_paychecks_before(point.day, paycheck_days))
            balance = point.balance + line.planned_per_paycheck * landed
            if balance < 0:
                breaches.append(
                    {
                        "account": "bucket",
                        "account_name": line.account_name,
                        "when": point.when,
                        "balance": balance.quantize(Decimal("0.01")),
                        "floor": Decimal("0.00"),
                    }
                )
                break

    return breaches


def _levers(
    lines: list[AccountPlan], shortfall: Decimal, capacity: Decimal
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
                "what": f"Reduce what {line.contribution} must hold",
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
