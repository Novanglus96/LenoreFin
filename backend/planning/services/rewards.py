"""What the credit cards will hand back, and when.

Card rewards are the household's Christmas fund. They accrue quietly all year
and are redeemed in one go in November, which is both the largest single inflow
the gift budget sees and completely invisible to the planner — so the plan asks
for money that will not be needed.

They are invisible for a specific reason worth knowing. A redemption is
sometimes recorded as a `Statement Credit` income transaction and sometimes not:
2019, 2020, 2021 and 2024 have them, 2025 does not, even though the balances
plainly dropped by 1,107.55 that November. The transaction record cannot be
relied on. The `Reward` table can — it is a running snapshot of each card's
balance, 621 of them, and a redemption shows up as an unmistakable cliff.

So this reads the balances directly and infers three things from the series:
what is accruing, when it gets spent, and therefore how much will be there when
it is. Nothing here is user-entered, because none of it needs to be.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from accounts.models import Reward

# How far back to read the balance history. Two years gives two redemptions,
# which is the fewest that can establish a rhythm rather than an anecdote.
LOOKBACK_DAYS = 760

# A fall in the balance this large is a redemption rather than an adjustment.
# Real redemptions here run 230 to 471 a card; the largest downward wobble that
# is not one is a couple of dollars.
REDEMPTION_DROP = Decimal("20")


@dataclass
class RewardOutlook:
    as_of: date
    current_balance: Decimal
    accrual_per_year: Decimal
    # When the cards have historically been cashed in, projected forward.
    redemption_on: date | None
    # The balance expected to be there by then: what is banked already, plus
    # what will accrue between now and the redemption.
    expected_amount: Decimal
    accounts: list[dict] = field(default_factory=list)
    past_redemptions: list[dict] = field(default_factory=list)


def _series(today: date) -> dict[int, list[tuple[date, Decimal, str]]]:
    window = today - timedelta(days=LOOKBACK_DAYS)
    out: dict[int, list[tuple[date, Decimal, str]]] = {}
    for reward in (
        Reward.objects.filter(reward_date__gte=window)
        .select_related("reward_account")
        .order_by("reward_date", "id")
    ):
        if reward.reward_amount is None:
            continue
        out.setdefault(reward.reward_account_id, []).append(
            (
                reward.reward_date,
                reward.reward_amount,
                reward.reward_account.account_name,
            )
        )
    return out


def reward_outlook(today: date) -> RewardOutlook:
    """Read the balance history and say what will be there in November.

    Accrual is the sum of the upward steps, annualised over the span actually
    observed — not the difference between the first and last balance, which
    would net off every redemption and report a card that earns 470 a year as
    earning nothing.
    """
    series = _series(today)
    total_accrual = Decimal("0")
    total_balance = Decimal("0")
    accounts: list[dict] = []
    redemptions: list[dict] = []

    for points in series.values():
        if len(points) < 2:
            continue
        name = points[-1][2]
        gained = Decimal("0")
        previous = None
        for when, amount, _ in points:
            if previous is not None:
                step = amount - previous
                if step > 0:
                    gained += step
                elif -step >= REDEMPTION_DROP:
                    redemptions.append(
                        {"when": when, "amount": -step, "account": name}
                    )
            previous = amount

        span = (points[-1][0] - points[0][0]).days or 1
        per_year = (gained * Decimal(365) / Decimal(span)).quantize(
            Decimal("0.01")
        )
        balance = points[-1][1]
        if per_year <= 0 and balance <= 0:
            continue
        total_accrual += per_year
        total_balance += balance
        accounts.append(
            {
                "account": name,
                "balance": balance,
                "as_of": points[-1][0],
                "accrual_per_year": per_year,
            }
        )

    redemptions.sort(key=lambda r: r["when"])
    redemption_on = _next_redemption(redemptions, today)

    expected = total_balance
    if redemption_on:
        days = Decimal((redemption_on - today).days)
        if days > 0:
            expected += total_accrual * days / Decimal(365)

    return RewardOutlook(
        as_of=today,
        current_balance=total_balance.quantize(Decimal("0.01")),
        accrual_per_year=total_accrual.quantize(Decimal("0.01")),
        redemption_on=redemption_on,
        expected_amount=expected.quantize(Decimal("0.01")),
        accounts=sorted(
            accounts, key=lambda a: a["accrual_per_year"], reverse=True
        ),
        past_redemptions=redemptions,
    )


def _next_redemption(redemptions: list[dict], today: date) -> date | None:
    """The next time the cards are likely to be cashed in.

    Taken from the day of the year they have been cashed in before, rather than
    from a date anyone typed. Several cards are redeemed within a few days of
    each other, so the redemptions cluster; the median day of that cluster is a
    better guess than the earliest or the latest.
    """
    if not redemptions:
        return None

    days = sorted(r["when"].timetuple().tm_yday for r in redemptions)
    typical = days[len(days) // 2]

    for year in (today.year, today.year + 1):
        candidate = date(year, 1, 1) + timedelta(days=typical - 1)
        if candidate >= today:
            return candidate
    return None
