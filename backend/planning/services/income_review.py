"""What the income reminders say against what actually landed.

The plan builds its capacity from the reminders: a paycheck reminder of
1,272.29 means the year affords 26 of those. If the reminder is stale, every
figure downstream is wrong in the same direction, and nothing anywhere says so
— the plan simply reports a smaller household than the one that exists. On this
data the two payroll reminders understate what arrives by about 340 a payday,
8,850 a year, which is the same order as the shortfall the plan was reporting.

The measurement is deliberately conservative about *which* figure to offer.

- The **median** is what a typical payday brings, and it is what an updated
  reminder should say. It ignores the overtime spikes rather than banking them.
- The **mean** is reported beside it, because the difference between the two is
  exactly the money that arrives unpredictably — worth seeing, never worth
  planning on. A plan that depends on overtime is not a plan.

Nothing here changes a reminder. Whether the typical paycheck has really moved,
or whether a good few months flattered the median, is a judgement about a job
rather than about arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from statistics import median

from django.db.models import Q

from reminders.models import Reminder
from transactions.models import Transaction

# Below these a difference is noise rather than a stale figure. Both have to be
# cleared: 10% of a small deposit is pennies, and 25 on a paycheck is a payroll
# rounding difference rather than a raise.
MATERIAL_FRACTION = Decimal("0.10")
MATERIAL_AMOUNT = Decimal("25")

# Fewer than this and the median is not a measurement, it is an anecdote.
MIN_DEPOSITS = 6


@dataclass
class IncomeDrift:
    """One income reminder measured against what actually arrived."""

    reminder_id: int
    description: str
    planned_amount: Decimal
    # What a typical deposit was. The figure an updated reminder should carry.
    median_amount: Decimal
    # What they averaged, overtime and all. Always >= median when the extra
    # money is upside; the gap between the two is what not to plan on.
    mean_amount: Decimal
    deposits: int
    # Per deposit, against the reminder. Positive means the plan is understating
    # this income.
    drift: Decimal
    # The same across a year of this reminder's cadence.
    drift_per_year: Decimal
    upside_per_deposit: Decimal
    why: str


@dataclass
class IncomeReview:
    generated_for: date
    window_days: int
    drifts: list[IncomeDrift] = field(default_factory=list)


def review_income(
    today: date, account_id: int | None, window_days: int = 365
) -> IncomeReview:
    """Every income reminder on the funding account, against its deposits."""
    from planning.services.planner import occurrences_per_year

    review = IncomeReview(generated_for=today, window_days=window_days)
    if account_id is None:
        return review

    since = today - timedelta(days=window_days)
    reminders = Reminder.objects.filter(
        Q(reminder_source_account_id=account_id)
        | Q(reminder_destination_account_id=account_id),
        transaction_type__slug="income",
    ).select_related("repeat")

    for reminder in reminders:
        if not reminder.description:
            continue
        # Matched by description, because a recorded Transaction carries no link
        # back to the reminder that produced it — only forecast rows do.
        amounts = [
            Decimal(str(t.total_amount))
            for t in Transaction.objects.filter(
                description=reminder.description,
                transaction_date__gte=since,
                transaction_date__lt=today,
            ).exclude(status__slug="archived")
            if t.total_amount
        ]
        if len(amounts) < MIN_DEPOSITS:
            continue

        planned = abs(Decimal(str(reminder.amount or 0)))
        if planned <= 0:
            continue
        typical = Decimal(str(median(sorted(amounts)))).quantize(Decimal("0.01"))
        average = (sum(amounts) / len(amounts)).quantize(Decimal("0.01"))
        drift = (typical - planned).quantize(Decimal("0.01"))
        if abs(drift) < MATERIAL_AMOUNT:
            continue
        if abs(drift) / planned < MATERIAL_FRACTION:
            continue

        per_year = occurrences_per_year(reminder.repeat) or Decimal("26.0893")
        upside = (average - typical).quantize(Decimal("0.01"))
        direction = "understating" if drift > 0 else "overstating"
        review.drifts.append(
            IncomeDrift(
                reminder_id=reminder.id,
                description=reminder.description,
                planned_amount=planned,
                median_amount=typical,
                mean_amount=average,
                deposits=len(amounts),
                drift=drift,
                drift_per_year=(drift * per_year).quantize(Decimal("0.01")),
                upside_per_deposit=upside,
                why=(
                    f"{reminder.description} is set to {planned}, but the last "
                    f"{len(amounts)} came in at {typical} typically — the plan "
                    f"is {direction} this income by {abs(drift)} a time, about "
                    f"{abs(drift * per_year).quantize(Decimal('0.01'))} a year."
                    + (
                        f" They averaged {average}, so about {upside} a time "
                        f"arrives on top of that and is not worth planning on."
                        if upside >= MATERIAL_AMOUNT
                        else ""
                    )
                ),
            )
        )
    review.drifts.sort(key=lambda d: -abs(d.drift_per_year))
    return review
