"""The savings plan: simulate every bucket over a window of paychecks.

The forecast is already the household's trusted view of the future — it
projects every reminder, recorded transaction and card payment. The plan does
not second-guess it. It takes each account's forecast, removes the transfers
the plan is deciding (each bucket's funding reminders, from the first paycheck
of the window on), puts the planned transfers in their place, and judges what
comes out:

- **Insolvent** — the funding account goes below zero, or a bucket stays below
  zero across more than one paycheck (or never recovers).
- **Workable** — a bucket dips below zero but the next paycheck clears it.
- **Ideal** — nothing goes below zero.

Goals are soft, and a plan stands as written until the next review. A bucket
that reaches its goal keeps being funded — the plan warns when it gets there
and what continuing costs, but does not assume anyone stops the transfer. A
bucket that ends short is flagged, with the shortfall, as somewhere a windfall
should go — never as a failure.

Expensive part: one forecast per account (~150ms each). That is computed once
per window and data version and cached, so re-simulating an edited plan is
arithmetic only and can follow every keystroke.
"""

from __future__ import annotations

import bisect
import hashlib
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from django.core.cache import cache
from django.db.models import Count, Max, Q

from accounts.models import Account
from planning.models import AcceptedBucket, Bucket, WindfallRule
from reminders.models import Reminder
from transactions.models import (
    ForecastCacheTransaction,
    ReminderCacheTransaction,
    Transaction,
)
from transactions.services.transactions_and_balances import (
    get_account_transactions_and_balances,
)
from utils.dates import forecast_horizon

ZERO = Decimal("0.00")
CENT = Decimal("0.01")
# A bucket may sit below zero across at most this many paydays and still be
# "workable": the next paycheck's transfer clears it.
MAX_DIP_PAYDAYS = 1
# How many days after its paycheck an existing transfer may land and still be
# that paycheck's transfer (this household's land the next day).
TRANSFER_LAG_DAYS = 6
BASELINE_TTL = 60 * 30
# Bump when the way a baseline is computed changes, so cached ones are dropped.
BASELINE_VERSION = 2

IDEAL = "ideal"
WORKABLE = "workable"
INSOLVENT = "insolvent"
_RANK = {IDEAL: 0, WORKABLE: 1, INSOLVENT: 2}


def _q(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(CENT)


# --------------------------------------------------------------------------
# Who pays, and when


def funding_account_id() -> int | None:
    """The account the buckets are paid from.

    The one most bucket reminders draw on; failing that, the account most
    paychecks land in.
    """
    sources = Counter(
        b.reminder.reminder_source_account_id
        for b in Bucket.objects.filter(active=True, reminder__isnull=False)
        .select_related("reminder")
        if b.reminder.reminder_source_account_id
    )
    if sources:
        return sources.most_common(1)[0][0]
    incomes = Counter(
        Reminder.objects.filter(transaction_type__slug="income").values_list(
            "reminder_source_account_id", flat=True
        )
    )
    return incomes.most_common(1)[0][0] if incomes else None


def _period_days(repeat) -> int:
    if repeat is None:
        return 0
    return int(
        (repeat.days or 0)
        + (repeat.weeks or 0) * 7
        + (repeat.months or 0) * 30
        + (repeat.years or 0) * 365
    )


def _income_reminders(account_id: int):
    return Reminder.objects.filter(
        Q(reminder_source_account_id=account_id)
        | Q(reminder_destination_account_id=account_id),
        transaction_type__slug="income",
    ).select_related("repeat")


def pay_calendar(today: date, end_date: date, account_id: int) -> list[date]:
    """Every payday from today to `end_date`, one entry per date.

    Two earners paid on the same day is one payday: everything here is "per
    paycheck", and that is the unit the household budgets in.
    """
    dates: set[date] = set()
    for reminder in _income_reminders(account_id):
        if reminder.end_date and reminder.end_date < today:
            continue
        step = _period_days(reminder.repeat)
        if step <= 0:
            continue
        cursor = reminder.next_date or reminder.start_date or today
        last = min(end_date, reminder.end_date or end_date)
        guard = 0
        while cursor <= last and guard < 1000:
            if cursor >= today:
                dates.add(cursor)
            cursor += timedelta(days=step)
            guard += 1
    return sorted(dates)


def pay_repeat_id(account_id: int) -> int | None:
    """The cadence new funding reminders should follow: the paychecks'."""
    for reminder in _income_reminders(account_id):
        if _period_days(reminder.repeat) > 0:
            return reminder.repeat_id
    return None


# --------------------------------------------------------------------------
# The window


@dataclass
class Window:
    start: date  # the first payday of the plan
    end: date  # last day modelled
    paydays: list[date]  # paydays inside [start, end]
    options: list[date]  # every payday that could start or end a window
    horizon: date  # how far the forecast reaches


def default_window_start(today: date, paydays: list[date]) -> date | None:
    """From October, the first payday of next year; otherwise the next payday."""
    if not paydays:
        return None
    if today.month >= 10:
        for payday in paydays:
            if payday.year > today.year:
                return payday
    return paydays[0]


def resolve_window(
    today: date,
    funding_id: int,
    start: date | None = None,
    end: date | None = None,
) -> Window:
    horizon = forecast_horizon(today)
    options = pay_calendar(today, horizon, funding_id)
    if start is None:
        start = default_window_start(today, options) or today
    else:
        # Snap to a real payday on or after what was asked for.
        later = [p for p in options if p >= start]
        start = later[0] if later else start
    if end is None:
        end = date(start.year, 12, 31)
    end = min(end, horizon)
    if end < start:
        end = start
    paydays = [p for p in options if start <= p <= end]
    return Window(start=start, end=end, paydays=paydays, options=options, horizon=horizon)


# --------------------------------------------------------------------------
# Which reminders the plan owns


def managed_reminder_ids(bucket: Bucket) -> set[int]:
    """Every reminder that funds this bucket on the plan's behalf.

    The bucket's own reminder, plus every reminder a standing acceptance
    wrote for it. Without the second set, re-planning after accepting would
    count a stop-at-goal schedule twice.
    """
    ids: set[int] = set()
    if bucket.reminder_id:
        ids.add(bucket.reminder_id)
    if bucket.pk:
        ids.update(
            AcceptedBucket.objects.filter(
                bucket=bucket, acceptance__reverted_on__isnull=True
            ).values_list("created_reminders", flat=True)
        )
    ids.discard(None)
    return set(Reminder.objects.filter(pk__in=ids).values_list("pk", flat=True))


def by_paycheck(
    items: list[tuple[date, Decimal]], paydays: list[date]
) -> dict[date, Decimal]:
    """Credit each transfer to the paycheck it belongs to.

    That is the latest payday on or before it. Existing transfers often land
    the day after payday; planned ones land on it. Comparing by paycheck
    rather than by date is what lets a re-stated amount read as unchanged.
    """
    out: dict[date, Decimal] = {}
    for when, amount in items:
        i = bisect.bisect_right(paydays, when) - 1
        if i < 0:
            continue
        out[paydays[i]] = out.get(paydays[i], ZERO) + amount
    return out


# --------------------------------------------------------------------------
# Baselines


@dataclass
class Baseline:
    """One account's forecast, as dated deltas."""

    account_id: int
    opening: Decimal
    rows: list[tuple[date, Decimal, int | None]]  # (date, delta, reminder_id)


def data_version() -> str:
    """Changes whenever anything the forecast reads has changed."""
    parts = []
    for model in (Transaction, ReminderCacheTransaction, ForecastCacheTransaction):
        agg = model.objects.aggregate(n=Count("id"), m=Max("id"))
        parts.append(f"{agg['n']}:{agg['m']}")
    parts.append(str(Transaction.objects.aggregate(m=Max("edit_date"))["m"]))
    parts.extend(
        f"{r[0]}:{r[1]}:{r[2]}:{r[3]}"
        for r in Reminder.objects.order_by("id").values_list(
            "id", "amount", "next_date", "end_date"
        )
    )
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:16]


def _compute_baseline(account_id: int, today: date, end: date) -> Baseline:
    # The forecast's end date is exclusive (`transaction_date < end_date`), so
    # ask for the day after: the window's last day — a payday, often — must be
    # in the forecast, or its planned transfers land with no paycheck to pay
    # for them.
    rows, opening = get_account_transactions_and_balances(
        end + timedelta(days=1), account_id, True, True, today, False
    )
    opening = _q(opening)
    previous = opening
    out: list[tuple[date, Decimal, int | None]] = []
    for row in rows:
        if row.balance is None or row.transaction_date is None:
            continue
        balance = _q(row.balance)
        out.append((row.transaction_date, balance - previous, row.reminder_id))
        previous = balance
    return Baseline(account_id=account_id, opening=opening, rows=out)


def load_baselines(
    account_ids: set[int], today: date, end: date
) -> dict[int, Baseline]:
    version = data_version()
    found: dict[int, Baseline] = {}
    for account_id in sorted(account_ids):
        key = (
            f"savings_plan:baseline:v{BASELINE_VERSION}:{version}:"
            f"{account_id}:{today}:{end}"
        )
        baseline = cache.get(key)
        if baseline is None:
            baseline = _compute_baseline(account_id, today, end)
            cache.set(key, baseline, BASELINE_TTL)
        found[account_id] = baseline
    return found


# --------------------------------------------------------------------------
# Plan input


@dataclass
class PlanEntry:
    """One bucket as the plan proposes it."""

    key: str  # "b<id>" for an existing bucket, "new<n>" for a draft
    name: str
    account_id: int | None
    per_paycheck: Decimal
    goal_amount: Decimal | None = None
    goal_date: date | None = None
    remove: bool = False
    bucket: Bucket | None = None
    managed: set[int] = field(default_factory=set)


def entries_from_buckets() -> list[PlanEntry]:
    return [
        PlanEntry(
            key=f"b{b.pk}",
            name=b.name,
            account_id=b.account_id,
            per_paycheck=_q(b.contribution_per_paycheck),
            goal_amount=_q(b.goal_amount) if b.goal_amount is not None else None,
            goal_date=b.goal_date,
            bucket=b,
        )
        for b in Bucket.objects.filter(active=True).select_related("reminder")
    ]


def apply_edits(entries: list[PlanEntry], edits: dict | None) -> list[PlanEntry]:
    """Overlay the page's edits on the stored buckets.

    `edits` = {"buckets": {"b12": {...}}, "new": [{...}], "remove": ["b3"]}.
    """
    edits = edits or {}
    by_key = {e.key: e for e in entries}
    for key, change in (edits.get("buckets") or {}).items():
        entry = by_key.get(key)
        if entry is None:
            continue
        if "per_paycheck" in change and change["per_paycheck"] is not None:
            entry.per_paycheck = _q(change["per_paycheck"])
        if "goal_amount" in change:
            value = change["goal_amount"]
            entry.goal_amount = _q(value) if value not in (None, "") else None
        if "goal_date" in change:
            entry.goal_date = change["goal_date"] or None
    for key in edits.get("remove") or []:
        if key in by_key:
            by_key[key].remove = True
    for n, draft in enumerate(edits.get("new") or []):
        goal = draft.get("goal_amount")
        entries.append(
            PlanEntry(
                key=draft.get("key") or f"new{n}",
                name=draft.get("name") or f"New bucket {n + 1}",
                account_id=draft.get("account_id"),
                per_paycheck=_q(draft.get("per_paycheck")),
                goal_amount=_q(goal) if goal not in (None, "") else None,
                goal_date=draft.get("goal_date") or None,
            )
        )
    return entries


def overage_order(entries: list[PlanEntry], overrides: list[str] | None = None) -> list[str]:
    """The order windfalls flow down, as entry keys.

    An explicit order from the page wins. Otherwise the stored windfall rules
    that name a bucket, in their order, then every other bucket with a goal.
    """
    keys = {e.key for e in entries if not e.remove}
    if overrides:
        ordered = [k for k in overrides if k in keys]
    else:
        ordered = [
            f"b{r.bucket_id}"
            for r in WindfallRule.objects.filter(bucket__isnull=False)
            if f"b{r.bucket_id}" in keys
        ]
    for entry in entries:
        if entry.key in keys and entry.goal_amount is not None and entry.key not in ordered:
            ordered.append(entry.key)
    return list(dict.fromkeys(ordered))


# --------------------------------------------------------------------------
# Judging a path


@dataclass
class Dip:
    start: date
    low: Decimal
    low_when: date
    recovers_on: date | None
    paydays_below: int

    @property
    def tolerable(self) -> bool:
        return self.recovers_on is not None and self.paydays_below <= MAX_DIP_PAYDAYS

    def as_dict(self) -> dict:
        return {
            "start": self.start,
            "low": self.low,
            "low_when": self.low_when,
            "recovers_on": self.recovers_on,
            "paydays_below": self.paydays_below,
            "tolerable": self.tolerable,
        }


def find_dips(points: list[tuple[date, Decimal]], paydays: list[date]) -> list[Dip]:
    """Every run below zero, with how many paydays land while it lasts.

    A payday on the day the dip opens is already in that day's closing
    balance, so it does not count as one the dip survived.
    """

    def landed(a: date, b: date) -> int:
        return bisect.bisect_right(paydays, b) - bisect.bisect_right(paydays, a)

    dips: list[Dip] = []
    current: Dip | None = None
    for when, balance in points:
        if balance < 0:
            if current is None:
                current = Dip(when, balance, when, None, 0)
            elif balance < current.low:
                current.low, current.low_when = balance, when
        elif current is not None:
            current.recovers_on = when
            current.paydays_below = landed(current.start, when)
            dips.append(current)
            current = None
    if current is not None:
        current.paydays_below = landed(current.start, points[-1][0])
        dips.append(current)
    return dips


def _verdict(dips: list[Dip], strict: bool) -> str:
    if not dips:
        return IDEAL
    if strict or any(not d.tolerable for d in dips):
        return INSOLVENT
    return WORKABLE


def _closing_path(
    opening: Decimal,
    events: list[tuple[date, Decimal]],
    today: date,
    end: date,
) -> list[tuple[date, Decimal]]:
    """One point per day that anything happens, holding the closing balance."""
    by_day: dict[date, Decimal] = {}
    running = opening
    for when, delta in sorted(events, key=lambda e: e[0]):
        running += delta
        by_day[when] = running
    points = [(today, opening)] + sorted(by_day.items())
    if points[-1][0] < end:
        points.append((end, running))
    return [(d, _q(b)) for d, b in points]


def _balance_on(points: list[tuple[date, Decimal]], when: date) -> Decimal:
    dates = [p[0] for p in points]
    i = bisect.bisect_right(dates, when) - 1
    return points[i][1] if i >= 0 else points[0][1]


# --------------------------------------------------------------------------
# The simulation


def _segments(schedule: list[tuple[date, Decimal]]) -> list[dict]:
    """Collapse a per-transfer schedule into runs of one amount."""
    runs: list[dict] = []
    for when, amount in schedule:
        if runs and runs[-1]["amount"] == amount:
            runs[-1]["end"] = when
            runs[-1]["count"] += 1
        else:
            runs.append({"start": when, "end": when, "amount": amount, "count": 1})
    return runs


def simulate(
    today: date,
    window: Window,
    entries: list[PlanEntry],
    overrides: list[str] | None = None,
    baselines: dict[int, Baseline] | None = None,
    funding_id: int | None = None,
) -> dict:
    if funding_id is None:
        funding_id = funding_account_id()
    for entry in entries:
        if entry.bucket is not None:
            entry.managed = managed_reminder_ids(entry.bucket)
    # Planned transfers land on the paycheck they come out of.
    transfer_dates = list(window.paydays)
    first_transfer = transfer_dates[0] if transfer_dates else window.start
    # A transfer that lands a few days after the window's last paychecks is
    # past the end of the forecast, so those paychecks are left out of the
    # changed-or-not comparison rather than read as missing.
    comparable = [p for p in transfer_dates if p + timedelta(days=TRANSFER_LAG_DAYS) <= window.end]

    accounts = {funding_id} | {e.account_id for e in entries if e.account_id}
    accounts.discard(None)
    if baselines is None:
        baselines = load_baselines(accounts, today, window.end)

    def stripped(account_id: int, removed: set[int]) -> list[tuple[date, Decimal]]:
        """The forecast without the plan-owned transfers from the window on."""
        return [
            (when, delta)
            for when, delta, rid in baselines[account_id].rows
            if not (rid in removed and when >= first_transfer)
        ]

    def current_events(account_id: int) -> list[tuple[date, Decimal]]:
        return [(w, d) for w, d, _ in baselines[account_id].rows]

    planned = [e for e in entries if not e.remove and e.account_id]
    order = overage_order(entries, overrides)

    # A plan stands, unchanged, until the household reviews it. Every bucket
    # is funded at its planned amount on every transfer of the window — even
    # after its goal is reached. Reaching a goal is a warning to act on at the
    # next review, never an assumption that the transfers stop by themselves.
    schedules: dict[str, list[tuple[date, Decimal]]] = {
        e.key: [(when, e.per_paycheck) for when in transfer_dates] for e in planned
    }

    # ---- Paths and verdicts
    buckets_out = []
    worst = IDEAL
    removed_managed: set[int] = set()
    for entry in entries:
        removed_managed |= entry.managed

    for entry in entries:
        out = {
            "key": entry.key,
            "bucket_id": entry.bucket.pk if entry.bucket else None,
            "name": entry.name,
            "account_id": entry.account_id,
            "account_name": None,
            "current_per_paycheck": _q(entry.bucket.contribution_per_paycheck)
            if entry.bucket
            else ZERO,
            "planned_per_paycheck": entry.per_paycheck,
            "goal_amount": entry.goal_amount,
            "goal_date": entry.goal_date,
            "is_new": entry.bucket is None,
            "removed": entry.remove,
            "linked": bool(entry.account_id),
            "has_reminder": bool(entry.managed),
        }
        if entry.account_id:
            out["account_name"] = (
                Account.objects.filter(pk=entry.account_id)
                .values_list("account_name", flat=True)
                .first()
            )
        if entry.remove or not entry.account_id:
            out.update(
                verdict=None, path=[], current_path=[], segments=[],
                current_segments=[], dips=[], changed=entry.remove,
            )
            buckets_out.append(out)
            continue

        events = stripped(entry.account_id, entry.managed) + schedules[entry.key]
        path = _closing_path(baselines[entry.account_id].opening, events, today, window.end)
        current = _closing_path(
            baselines[entry.account_id].opening,
            current_events(entry.account_id),
            today,
            window.end,
        )
        in_window = [p for p in path if p[0] >= window.start]
        dips = find_dips(in_window, transfer_dates)
        verdict = _verdict(dips, strict=False)
        if _RANK[verdict] > _RANK[worst]:
            worst = verdict

        judged_on = entry.goal_date or window.end
        at_goal_date = _balance_on(path, min(judged_on, window.end))
        shortfall = (
            max(ZERO, entry.goal_amount - at_goal_date)
            if entry.goal_amount is not None
            else None
        )
        low = min(in_window, key=lambda p: p[1]) if in_window else (today, ZERO)
        # The first day in the window the balance reaches the goal, and what the
        # plan keeps paying in after that — the warning, with its cost.
        reached_on = None
        if entry.goal_amount is not None:
            reached_on = next(
                (d for d, b in in_window if b >= entry.goal_amount), None
            )
        paid_after_goal = (
            sum((a for w, a in schedules[entry.key] if w > reached_on), ZERO)
            if reached_on
            else ZERO
        )
        # What the bucket's reminders already deliver in the window, so accept
        # can tell a real change from a re-statement of what is scheduled.
        now = by_paycheck(
            [
                (when, delta)
                for when, delta, rid in baselines[entry.account_id].rows
                if rid in entry.managed and when >= first_transfer
            ],
            transfer_dates,
        )
        planned_now = by_paycheck(schedules[entry.key], transfer_dates)
        out.update(
            verdict=verdict,
            path=path,
            current_path=current,
            segments=_segments(schedules[entry.key]),
            current_segments=_segments(sorted(now.items())),
            changed=any(
                planned_now.get(p, ZERO) != now.get(p, ZERO) for p in comparable
            ),
            dips=[d.as_dict() for d in dips],
            start_balance=_balance_on(path, window.start),
            end_balance=path[-1][1],
            low_balance=low[1],
            low_when=low[0],
            goal_reached_on=reached_on,
            paid_after_goal=paid_after_goal,
            balance_at_goal_date=at_goal_date,
            shortfall=shortfall,
            received_in_window=sum((a for _, a in schedules[entry.key]), ZERO),
        )
        buckets_out.append(out)

    # ---- The funding account: never below zero, not even for a day.
    funding_out = None
    if funding_id:
        events = stripped(funding_id, removed_managed)
        for entry in planned:
            events += [(w, -a) for w, a in schedules[entry.key]]
        path = _closing_path(baselines[funding_id].opening, events, today, window.end)
        current = _closing_path(
            baselines[funding_id].opening, current_events(funding_id), today, window.end
        )
        in_window = [p for p in path if p[0] >= window.start]
        before = [p for p in path if p[0] < window.start]
        dips = find_dips(in_window, window.paydays)
        verdict = _verdict(dips, strict=True)
        if _RANK[verdict] > _RANK[worst]:
            worst = verdict
        low = min(in_window, key=lambda p: p[1]) if in_window else (today, ZERO)
        funding_out = {
            "account_id": funding_id,
            "account_name": Account.objects.filter(pk=funding_id)
            .values_list("account_name", flat=True)
            .first(),
            "verdict": verdict,
            "path": path,
            "current_path": current,
            "dips": [d.as_dict() for d in dips],
            "low_balance": low[1],
            "low_when": low[0],
            "start_balance": _balance_on(path, window.start),
            "end_balance": path[-1][1],
            "negative_before_window": any(b < 0 for _, b in before),
        }

    # ---- Where windfalls should go: buckets short of their goals.
    stored_caps = {
        f"b{r.bucket_id}": r.cap_amount
        for r in WindfallRule.objects.filter(bucket__isnull=False)
    }
    names = {b["key"]: b["name"] for b in buckets_out}
    gaps = {b["key"]: b.get("shortfall") for b in buckets_out}
    suggested_rules = [
        {
            "key": key,
            "name": names[key],
            # Calculated: what the goal still needs at its date under this plan.
            # None for a bucket with no goal, which takes the remainder.
            "shortfall": gaps.get(key),
            # A cap the owner set, which overrides the calculation.
            "cap_amount": stored_caps.get(key),
        }
        for key in order
        if key in names
    ]

    total_current = sum(
        (_q(e.bucket.contribution_per_paycheck) for e in entries if e.bucket), ZERO
    )
    total_planned = sum((e.per_paycheck for e in planned), ZERO)
    return {
        "today": today,
        "window": {
            "start": window.start,
            "end": window.end,
            "paydays": len(window.paydays),
            "first_transfer": first_transfer,
            "options": window.options,
            "horizon": window.horizon,
        },
        "verdict": worst,
        "total_current_per_paycheck": total_current,
        "total_planned_per_paycheck": total_planned,
        "funding": funding_out,
        "buckets": buckets_out,
        "overage_order": order,
        "suggested_rules": suggested_rules,
    }


def build_plan(
    today: date,
    start: date | None = None,
    end: date | None = None,
    edits: dict | None = None,
) -> dict:
    funding_id = funding_account_id()
    if funding_id is None:
        return {"error": "No funding account: link a bucket to its transfer first."}
    window = resolve_window(today, funding_id, start, end)
    entries = apply_edits(entries_from_buckets(), edits)
    overrides = (edits or {}).get("overage_order")
    return simulate(today, window, entries, overrides)
