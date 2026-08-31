"""What counts as an account going negative.

The rule these tests encode is the owner's, not an arithmetic convenience:

    Small dips or short periods that can be covered by moving money are
    acceptable. Those are just timing issues if at the end of the plan the
    account is rectified.

So a dip is only a *failure* when the account never climbs back out, or when it
is still under water after the money has had two paydays to arrive. Everything
else is a transfer to schedule, and the tests below pin that distinction down
because getting it wrong tells someone to cut their savings over a fortnight's
bad timing.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from planning.services.savings_plan import (
    MAX_BRIDGES_PER_YEAR,
    PathPoint,
    allocatable_per_paycheck,
    capacity_per_paycheck,
    find_dips,
)

TODAY = date(2026, 1, 1)
FLOOR = Decimal("10.00")


def points(*pairs):
    """`(day, balance)` pairs as the `(day, date, balance)` triples dips take."""
    return [
        (day, TODAY + timedelta(days=day), Decimal(str(balance)))
        for day, balance in pairs
    ]


def path(*pairs):
    return [
        PathPoint(day=day, when=TODAY + timedelta(days=day), balance=Decimal(str(b)))
        for day, b in pairs
    ]


# Paydays every 14 days for a year, the cadence this household is actually paid.
PAYDAYS = list(range(14, 366, 14))


@pytest.mark.service
def test_a_path_that_never_goes_under_has_no_dips():
    assert find_dips(points((0, 500), (30, 200), (60, 11)), FLOOR, PAYDAYS) == []


@pytest.mark.service
def test_a_dip_that_recovers_is_a_timing_problem():
    dips = find_dips(
        points((0, 500), (20, -100), (24, 300)),
        FLOOR,
        PAYDAYS,
    )

    assert len(dips) == 1
    dip = dips[0]
    assert dip.kind == "one_off"
    assert dip.start == TODAY + timedelta(days=20)
    assert dip.recovers_on == TODAY + timedelta(days=24)
    assert dip.days_below == 4
    # The bridge is measured to the floor, not to zero: leaving the account at
    # nought is not leaving it healthy.
    assert dip.depth == Decimal("110.00")


@pytest.mark.service
def test_the_bridge_is_sized_from_the_deepest_point_not_the_first():
    dips = find_dips(
        points((0, 500), (20, -50), (22, -300), (26, -80), (30, 400)),
        FLOOR,
        PAYDAYS,
    )

    assert len(dips) == 1
    assert dips[0].depth == Decimal("310.00")
    assert dips[0].low_when == TODAY + timedelta(days=22)
    # ...while the transfer still has to land before the dip *opens*.
    assert dips[0].start == TODAY + timedelta(days=20)


@pytest.mark.service
def test_an_account_that_never_recovers_is_structural():
    dips = find_dips(points((0, 500), (100, -200), (365, -900)), FLOOR, PAYDAYS)

    assert len(dips) == 1
    assert dips[0].kind == "structural"
    assert dips[0].recovers_on is None
    assert "never recovers" in dips[0].why


@pytest.mark.service
def test_still_under_water_after_three_paydays_is_structural():
    # Opens on day 15, recovers on day 60: paydays land on 28, 42 and 56 while
    # the account is under. Money has arrived three times and not fixed it.
    dips = find_dips(points((0, 500), (15, -100), (60, 300)), FLOOR, PAYDAYS)

    assert len(dips) == 1
    assert dips[0].paydays_below == 3
    assert dips[0].kind == "structural"
    assert "not a timing gap" in dips[0].why


@pytest.mark.service
def test_two_paydays_under_water_is_still_only_timing():
    # Opens day 15, recovers day 45: paydays on 28 and 42. Two is the boundary
    # and the boundary is inclusive.
    dips = find_dips(points((0, 500), (15, -100), (45, 300)), FLOOR, PAYDAYS)

    assert dips[0].paydays_below == 2
    assert dips[0].kind == "one_off"


@pytest.mark.service
def test_separate_dips_are_reported_separately():
    dips = find_dips(
        points((0, 500), (20, -100), (24, 300), (200, -50), (204, 400)),
        FLOOR,
        PAYDAYS,
    )

    assert [d.kind for d in dips] == ["one_off", "one_off"]
    assert [d.depth for d in dips] == [Decimal("110.00"), Decimal("60.00")]


@pytest.mark.service
def test_a_dip_open_at_the_horizon_is_structural_however_shallow():
    # A penny under the floor on the last day is still an account the plan
    # never puts right, which is exactly what the owner's rule excludes.
    dips = find_dips(points((0, 500), (365, Decimal("9.99"))), FLOOR, PAYDAYS)

    assert dips[0].kind == "structural"


@pytest.mark.service
def test_allocation_stops_before_bridging_becomes_a_fortnightly_shuffle():
    """The whole point of the bridge budget.

    A funding account that empties and refills each cycle can be allocated
    right up to the year's surplus — and then it goes under in every cycle.
    Capacity has to stop short of that.
    """
    # Pay lands, the cycle's bills take all of it back, and the year's whole
    # surplus arrives as one lump in month twelve. Over the year there is
    # plenty; on any given Tuesday in June there is not.
    pairs = [(0, 3000)]
    balance = Decimal("3000")
    for day in range(14, 366, 14):
        balance += Decimal("2000")  # pay
        pairs.append((day, balance))
        balance -= Decimal("2000")  # bills, a week later
        pairs.append((day + 7, balance))
        if day == 350:
            balance += Decimal("6000")  # the annual bonus
            pairs.append((day + 8, balance))
    fund_path = path(*pairs)

    path_capacity, horizon_capacity, _, _ = capacity_per_paycheck(
        fund_path, FLOOR, PAYDAYS
    )
    assert path_capacity < horizon_capacity

    allocatable = allocatable_per_paycheck(
        fund_path, FLOOR, PAYDAYS, path_capacity, horizon_capacity, MAX_BRIDGES_PER_YEAR
    )

    assert path_capacity <= allocatable <= horizon_capacity
    dips = find_dips(
        [
            (
                p.day,
                p.when,
                p.balance
                - allocatable * Decimal(len([d for d in PAYDAYS if d <= p.day])),
            )
            for p in fund_path
        ],
        FLOOR,
        PAYDAYS,
    )
    assert len(dips) <= MAX_BRIDGES_PER_YEAR
    assert not any(d.kind == "structural" for d in dips)


@pytest.mark.service
def test_a_plan_needing_no_bridging_allocates_the_whole_surplus():
    """When the money is there all along, the bridge budget must not bite."""
    pairs = [(0, 50000)]
    balance = Decimal("50000")
    for day in range(14, 366, 14):
        balance += Decimal("100")
        pairs.append((day, balance))
    fund_path = path(*pairs)

    path_capacity, horizon_capacity, _, _ = capacity_per_paycheck(
        fund_path, FLOOR, PAYDAYS
    )
    allocatable = allocatable_per_paycheck(
        fund_path, FLOOR, PAYDAYS, path_capacity, horizon_capacity, MAX_BRIDGES_PER_YEAR
    )

    assert allocatable == horizon_capacity
