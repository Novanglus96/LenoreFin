"""How much a budget plans to spend, and which tags it speaks for.

Split out from the planner because three places need the same answers and they
have to agree: the savings plan funds from budgets, the budget review checks
budgets against reality, and the budgets page shows people what they said. A
parent budget that totals 1,130 in one of them and 1,995 in another is worse
than having no parent at all.

The rule everywhere: **a parent is the sum of its children, and only a parent
speaks.** Children are components. That is what makes it impossible for the
same spending to be counted twice — the situation this replaces, where a 1,995
Christmas budget and twenty-three per-person budgets covered the same tags and
nothing reconciled them.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

DAYS_PER_MONTH = Decimal("30.44")
DAYS_PER_YEAR = Decimal("365.25")


def period_days(repeat) -> Decimal:
    """How many days one turn of this repeat covers."""
    if repeat is None:
        return Decimal("0")
    return (
        Decimal(repeat.days or 0)
        + Decimal(repeat.weeks or 0) * 7
        + Decimal(repeat.months or 0) * DAYS_PER_MONTH
        + Decimal(repeat.years or 0) * DAYS_PER_YEAR
    )


def occurrences_per_year(repeat) -> Decimal:
    """How many times a year this repeat comes round.

    Months and years are converted exactly rather than through average day
    lengths. Twelve monthly payments are twelve a year, but 365.25 / 30.44 is
    11.999, which turns a 50-a-month budget into 599.95 a year. Five pence is
    nothing arithmetically and looks broken on a page about money.
    """
    if repeat is None:
        return Decimal("0")
    days = Decimal(repeat.days or 0)
    weeks = Decimal(repeat.weeks or 0)
    months = Decimal(repeat.months or 0)
    years = Decimal(repeat.years or 0)

    if not days and not weeks:
        if months and not years:
            return Decimal(12) / months
        if years and not months:
            return Decimal(1) / years

    period = period_days(repeat)
    if period <= 0:
        return Decimal("0")
    return DAYS_PER_YEAR / period


def amount_per_year(amount: Decimal | None, repeat) -> Decimal:
    """A budget's yearly cost, whatever cadence it is stated in."""
    per_year = occurrences_per_year(repeat)
    if per_year <= 0 or not amount:
        return Decimal("0.00")
    return (abs(amount) * per_year).quantize(Decimal("0.01"))


def parent_planned_amount(budget) -> Decimal:
    """The sum of a parent's children, expressed in the parent's own cadence.

    Converted through a yearly figure rather than added raw: a yearly parent
    over monthly children is a reasonable thing to want, and summing the face
    values would be out by a factor of twelve.
    """
    total_per_year = sum(
        (
            amount_per_year(child.amount, child.repeat)
            for child in budget.children.filter(active=True).select_related(
                "repeat"
            )
        ),
        Decimal("0.00"),
    )
    per_year = occurrences_per_year(budget.repeat)
    if per_year <= 0:
        return total_per_year.quantize(Decimal("0.01"))
    return (total_per_year / per_year).quantize(Decimal("0.01"))


def budget_tag_ids(budget) -> list[int]:
    """The tags a budget speaks for.

    A parent speaks for its own tags **and** its children's. Its own are kept
    rather than replaced because a parent often covers ground no child has
    claimed — this household's Christmas parent lists twenty-two tags while its
    children name one apiece, and dropping the parent's would silently stop
    funding whatever nobody wrote a line for.
    """
    ids: set[int] = set(_own_tag_ids(budget))
    if budget.pk:
        for child in budget.children.filter(active=True):
            ids.update(_own_tag_ids(child))
    return sorted(ids)


def _own_tag_ids(budget) -> list[int]:
    if not budget.tag_ids:
        return []
    try:
        parsed = json.loads(budget.tag_ids)
    except (ValueError, TypeError):
        return []
    return [int(t) for t in parsed] if isinstance(parsed, list) else []


def spending_budgets(queryset):
    """The budgets that speak: leaves and parents, never a child.

    A child's spending is already inside its parent's total, so counting both
    funds it twice — which is exactly the trap the old flat model set.
    """
    return [b for b in queryset if b.parent_id is None]


def budget_events(
    budget, today: date, end_date: date
) -> list[tuple[date, Decimal]]:
    """When a budget's spending lands, and how much.

    Dated events rather than a smooth rate, because when the money is needed
    decides how much has to be saved by then. Christmas proves it: 1,995 a year
    trickled evenly never requires the account to hold more than a couple of
    hundred, while the same sum landing in December means the whole lot has to
    be there by then.

    A parent defers to its children, so a child with its own cadence and start
    day lands when it actually lands instead of being averaged into the
    parent's rhythm.
    """
    from datetime import timedelta

    if budget.pk and budget.children.filter(active=True).exists():
        events: list[tuple[date, Decimal]] = []
        for child in budget.children.filter(active=True).select_related("repeat"):
            events.extend(budget_events(child, today, end_date))
        return sorted(events)

    period = period_days(budget.repeat)
    if period <= 0 or not budget.amount:
        return []

    step = int(period)
    cursor = budget.next_start or budget.start_day or today
    # A cycle that began before today is already part way through; the rest of
    # it still has to be funded.
    while cursor < today:
        cursor = cursor + timedelta(days=step)

    events = []
    guard = 0
    while cursor <= end_date and guard < 400:
        events.append((cursor, -abs(budget.amount)))
        cursor = cursor + timedelta(days=step)
        guard += 1
    return events
