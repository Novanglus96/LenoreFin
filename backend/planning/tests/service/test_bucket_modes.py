"""What a bucket is *for*, and what each answer costs.

Modes exist because one field was doing two jobs. `target_balance` with no date
meant "hold this from today"; with a date it meant "reach this by then". Those
are not variants of one intention — the first is a floor under every day of the
year and the second is a single constraint at one point — and on this
household's real data the difference was an order of magnitude a paycheck, all
of it drawn from whatever sat below in priority.

These tests pin the four modes to that distinction, and pin the note that asks
the question the migration deliberately could not.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from planning.models import BucketMode
from planning.services.savings_plan import PathPoint, _ambition

TODAY = date(2026, 1, 1)
END = date(2026, 12, 31)
PAYDAYS = list(range(14, 366, 14))


def flat(balance):
    """A year of daily closing balances, which is the shape `baseline_path`
    returns. Density matters here: the demand is evaluated at every point, and
    the binding one is the earliest payday that can be asked to carry the gap.
    A sparse path quietly understates what a floor costs.
    """
    return [
        PathPoint(day=d, when=TODAY + timedelta(days=d), balance=Decimal(str(balance)))
        for d in range(366)
    ]


class FakeBucket:
    """Only the fields `_ambition` reads. It never touches the database."""

    def __init__(self, mode, minimum_balance=None, goal_amount=None, goal_date=None):
        self.mode = mode
        self.minimum_balance = minimum_balance
        self.goal_amount = goal_amount
        self.goal_date = goal_date


# A bucket sitting flat at 1,000 all year, spending nothing.
FLAT = flat(1000)
BASE = Decimal("0.00")


@pytest.mark.service
def test_cover_asks_for_nothing_above_what_it_spends():
    target, reason, warning = _ambition(
        FakeBucket(BucketMode.COVER), FLAT, BASE, TODAY, END, PAYDAYS, ["Groceries"]
    )
    assert target == BASE
    assert reason == "Covering Groceries."
    assert warning is None


@pytest.mark.service
def test_cover_without_budgets_says_so():
    _, reason, _ = _ambition(
        FakeBucket(BucketMode.COVER), FLAT, BASE, TODAY, END, PAYDAYS, []
    )
    assert reason == "Covering its dated obligations."


@pytest.mark.service
def test_maximise_takes_the_remainder_and_asks_for_no_target():
    target, reason, warning = _ambition(
        FakeBucket(BucketMode.MAXIMISE), FLAT, BASE, TODAY, END, PAYDAYS, []
    )
    assert target == BASE
    assert "whatever is left" in reason
    assert warning is None


@pytest.mark.service
def test_maintain_funds_the_gap_to_its_floor_from_the_first_payday():
    """4,000 held from today against 1,000 on hand, over 26 paydays.

    The binding point is the earliest day the shortfall can be solved for at
    all — two paydays in — so two paychecks carry the whole 3,000 between them.
    Every later day is easier and none of them binds.
    """
    bucket = FakeBucket(BucketMode.MAINTAIN, minimum_balance=Decimal("4000"))
    target, reason, _ = _ambition(bucket, FLAT, BASE, TODAY, END, PAYDAYS, [])

    assert target == Decimal("1500.00")
    assert reason == "Holding at least 4000 from now on."


@pytest.mark.service
def test_the_same_money_wanted_by_a_date_costs_a_fraction_of_holding_it():
    """The whole reason modes exist, as one comparison.

    Identical bucket, identical 4,000, identical path. Held from today it wants
    1,500 a paycheck, because the gap has to close within two paydays to hold
    every day after them; wanted by the end of the year it wants 120, because
    all 26 paydays share the load. Twelve and a half times, from a date.
    """
    held = _ambition(
        FakeBucket(BucketMode.MAINTAIN, minimum_balance=Decimal("4000")),
        FLAT, BASE, TODAY, END, PAYDAYS, [],
    )[0]
    by_a_date = _ambition(
        FakeBucket(BucketMode.GOAL, goal_amount=Decimal("4000"), goal_date=END),
        FLAT, BASE, TODAY, END, PAYDAYS, [],
    )[0]

    assert held == Decimal("1500.00")
    assert by_a_date == Decimal("120.00")
    assert by_a_date < held / 10


@pytest.mark.service
def test_maintain_prices_the_alternative_rather_than_guessing_at_it():
    """The migration could not ask, so the plan asks — with the figure attached.

    A bucket that inherited Maintain from an undated target may never have been
    asked the question. Telling someone "this might be wrong" is worth little;
    telling them it costs 1,500 a paycheck and would cost 120 as a goal is the
    whole decision.
    """
    bucket = FakeBucket(BucketMode.MAINTAIN, minimum_balance=Decimal("4000"))
    _, _, warning = _ambition(bucket, FLAT, BASE, TODAY, END, PAYDAYS, [])

    assert warning is not None
    assert "1500.00 a paycheck" in warning
    assert "costs 120.00" in warning
    assert "switch this bucket to Goal" in warning


@pytest.mark.service
def test_a_maintain_that_is_already_covered_is_not_second_guessed():
    """No note where the floor costs nothing over the base.

    The suggestion is only worth making when the mode is actually driving the
    number. A bucket already holding more than its floor is not starving
    anything, and warning about it would be noise on every line.
    """
    bucket = FakeBucket(BucketMode.MAINTAIN, minimum_balance=Decimal("500"))
    target, _, warning = _ambition(bucket, FLAT, BASE, TODAY, END, PAYDAYS, [])

    assert target == BASE
    assert warning is None


@pytest.mark.service
def test_a_goal_never_falls_below_what_the_bucket_has_to_spend():
    """Ambition is above the base, never instead of it.

    A goal already satisfied by the balance on hand demands nothing of its own,
    but the bucket still has to cover its own spending.
    """
    base = Decimal("75.00")
    bucket = FakeBucket(BucketMode.GOAL, goal_amount=Decimal("500"), goal_date=END)
    target, _, _ = _ambition(bucket, FLAT, base, TODAY, END, PAYDAYS, [])

    assert target == base


@pytest.mark.service
def test_a_goal_whose_date_has_passed_says_so_instead_of_reading_as_free():
    """Zero here means "no longer solved for", not "achieved".

    `rate_to_reach` returns nothing for a date already gone, which on the plan
    line is indistinguishable from a goal comfortably met. The bucket is not
    funded and nothing anywhere would say why.
    """
    gone = TODAY - timedelta(days=30)
    bucket = FakeBucket(BucketMode.GOAL, goal_amount=Decimal("9000"), goal_date=gone)
    target, _, warning = _ambition(bucket, FLAT, BASE, TODAY, END, PAYDAYS, [])

    assert target == BASE
    assert warning is not None
    assert "has passed" in warning
