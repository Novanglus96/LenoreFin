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


# ---------------------------------------------------------------------------
# Bridging: where the money for a timing dip comes from
# ---------------------------------------------------------------------------


def a_line(bucket_id, account_id, name, lendable=True, priority=100):
    from planning.services.savings_plan import BucketPlan

    return BucketPlan(
        bucket_id=bucket_id,
        bucket_name=name,
        account_id=account_id,
        account_name=name,
        priority=priority,
        sweep=False,
        sweep_share=1,
        lendable=lendable,
        receives_rewards=False,
        paychecks_per_year=Decimal("26"),
        current_per_paycheck=Decimal("0"),
        minimum_per_paycheck=Decimal("0"),
        minimum_is_stated=False,
        target_per_paycheck=Decimal("0"),
        planned_per_paycheck=Decimal("0"),
        budgeted_per_paycheck=Decimal("0"),
        budget_names=[],
        target_balance=None,
        projected_low=Decimal("0"),
        projected_low_date=None,
        observed_spend_per_month=Decimal("0"),
        spend_variance_per_paycheck=Decimal("0"),
        reason="",
    )


def a_dip_breach(start_day, recover_day, needed):
    return {
        "account": "funding",
        "account_name": None,
        "kind": "one_off",
        "when": TODAY + timedelta(days=start_day),
        "low_when": TODAY + timedelta(days=start_day),
        "balance": Decimal("-1.00"),
        "floor": FLOOR,
        "one_off_needed": Decimal(str(needed)),
        "recovers_on": TODAY + timedelta(days=recover_day),
        "days_below": recover_day - start_day,
        "paydays_below": 0,
        "why": "",
    }


@pytest.mark.service
def test_a_balance_holds_until_something_moves_it():
    """The bug that made a bucket holding 15,000 unable to spare 26.

    Dips are short — three days is typical — and most accounts have nothing
    scheduled inside one. Judging an account only on the points that fall
    within the window means judging it on no points at all.
    """
    from planning.services.savings_plan import available_to_lend

    # One transaction, six weeks before the window opens, and nothing after.
    quiet = path((0, 15000), (300, 15000))

    spare = available_to_lend(quiet, Decimal("0"), PAYDAYS, 100, 103)

    assert spare == Decimal("15000.00")


@pytest.mark.service
def test_lending_is_limited_by_the_low_point_while_the_money_is_out():
    """Not by what the account holds on the day the money is wanted.

    An account with 900 today and a 850 bill on Thursday can lend 50 over a
    window that spans Thursday, however comfortable today looks.
    """
    from planning.services.savings_plan import available_to_lend

    lumpy = path((0, 900), (102, 50), (120, 4000))

    assert available_to_lend(lumpy, Decimal("0"), PAYDAYS, 100, 110) == Decimal(
        "50.00"
    )
    # Repaid before the bill lands, the whole 900 is available.
    assert available_to_lend(lumpy, Decimal("0"), PAYDAYS, 100, 102) == Decimal(
        "900.00"
    )


@pytest.mark.service
@pytest.mark.django_db
def test_a_protected_account_is_never_borrowed_from():
    from planning.services.savings_plan import solve_bridges

    breaches = [a_dip_breach(100, 103, "500.00")]
    lines = [
        a_line(1, 11, "Ellie's Savings", lendable=False),
        a_line(2, 12, "Ally - Reno", lendable=True),
    ]
    paths = {1: path((0, 90000)), 2: path((0, 500))}

    bridges = solve_bridges(breaches, lines, paths, PAYDAYS, 42, TODAY)

    assert len(bridges) == 1
    assert [m["from_account"] for m in bridges[0]["movements"]] == ["Ally - Reno"]
    assert bridges[0]["shortfall"] == Decimal("0.00")
    assert breaches[0]["kind"] == "one_off"


@pytest.mark.service
@pytest.mark.django_db
def test_an_unfundable_dip_stops_being_a_timing_problem():
    """The escalation the classifier deliberately leaves open.

    Depth never decides whether a dip is survivable — being able to cover it
    does. So a dip nobody can fund is reclassified, and that is what makes the
    plan fail verification instead of shipping advice to make an impossible
    transfer.
    """
    from planning.services.savings_plan import solve_bridges

    breaches = [a_dip_breach(100, 103, "500.00")]
    lines = [a_line(1, 11, "Ellie's Savings", lendable=False)]
    paths = {1: path((0, 90000))}

    bridges = solve_bridges(breaches, lines, paths, PAYDAYS, 42, TODAY)

    assert breaches[0]["kind"] == "structural"
    assert bridges[0]["shortfall"] == Decimal("500.00")
    # And it says which protected account would have covered it — a claim
    # about a balance, so it is measured rather than assumed.
    assert "Ellie's Savings could cover the rest" in breaches[0]["why"]


@pytest.mark.service
@pytest.mark.django_db
def test_a_bridge_is_split_across_sources_when_no_one_can_cover_it():
    from planning.services.savings_plan import solve_bridges

    breaches = [a_dip_breach(100, 103, "500.00")]
    lines = [
        a_line(1, 11, "Ally - Pet", priority=200),
        a_line(2, 12, "Ally - Reno", priority=300),
    ]
    paths = {1: path((0, 200)), 2: path((0, 400))}

    bridges = solve_bridges(breaches, lines, paths, PAYDAYS, 42, TODAY)

    movements = bridges[0]["movements"]
    assert bridges[0]["shortfall"] == Decimal("0.00")
    assert sum(m["amount"] for m in movements) == Decimal("500.00")
    # Least important first, so the bucket nobody is counting on gives first.
    assert movements[0]["from_account"] == "Ally - Reno"
    assert movements[0]["amount"] == Decimal("400.00")
    assert movements[1]["amount"] == Decimal("100.00")


@pytest.mark.service
@pytest.mark.django_db
def test_the_loan_runs_for_exactly_as_long_as_the_dip():
    """Repaying on the recovery date returns the funding path to what it was.

    That path was already proved to hold from the recovery date onward, so the
    repayment can never cause the next dip — which is why the window is the
    dip's own span rather than a policy someone has to choose.
    """
    from planning.services.savings_plan import solve_bridges

    breaches = [a_dip_breach(100, 117, "500.00")]
    lines = [a_line(1, 11, "Ally - Reno")]
    paths = {1: path((0, 5000))}

    bridges = solve_bridges(breaches, lines, paths, PAYDAYS, 42, TODAY)

    assert bridges[0]["when"] == TODAY + timedelta(days=100)
    assert bridges[0]["return_on"] == TODAY + timedelta(days=117)


# ---------------------------------------------------------------------------
# Rounding: figures a person can actually set up at a bank
# ---------------------------------------------------------------------------


@pytest.mark.service
def test_rounding_goes_the_way_that_keeps_the_promise():
    """Direction is not a style question here.

    A minimum rounded down is short by construction. Discretionary filling
    rounded up is what tipped this household's plan to 2,895 against the
    2,893.11 the year afforded — a plan made unaffordable by tidying it.
    """
    from planning.services.savings_plan import round_down_to, round_up_to

    assert round_up_to(Decimal("156.37")) == Decimal("160.00")
    assert round_down_to(Decimal("156.37")) == Decimal("155.00")
    # Already on the increment, so neither direction moves it.
    assert round_up_to(Decimal("150.00")) == Decimal("150.00")
    assert round_down_to(Decimal("150.00")) == Decimal("150.00")
    # Never below nothing: a negative allocation is not a bucket.
    assert round_down_to(Decimal("2.50")) == Decimal("0.00")
    assert round_down_to(Decimal("-40.00")) == Decimal("0.00")


@pytest.mark.service
def test_a_bridge_is_rounded_up_because_a_gap_is_not_nearly_covered():
    from planning.services.savings_plan import find_dips, round_up_to

    dips = find_dips(points((0, 500), (20, Decimal("-106.02")), (24, 300)), FLOOR, PAYDAYS)

    assert dips[0].depth == Decimal("116.02")
    # The measurement stays exact; the remedy is a transfer somebody makes.
    assert round_up_to(dips[0].depth) == Decimal("120.00")
    assert "Moving 120.00 in" in dips[0].why


# ---------------------------------------------------------------------------
# Sweeps: dividing what is left over
# ---------------------------------------------------------------------------


@pytest.mark.service
def test_sweeps_divide_the_remainder_by_weight():
    """Two accounts absorbing the leftover are rarely equally deserving of it.

    A house-projects fund being deliberately propped up and a child's savings
    account are not the same claim, and before there was a way to say so the
    split was decided by hand every time.
    """
    from planning.services.savings_plan import round_down_to

    remaining = Decimal("400.00")
    shares = {"Reno": 3, "Ellie's Savings": 1}
    total_share = sum(shares.values())

    given = {
        name: round_down_to(remaining * Decimal(share) / Decimal(total_share))
        for name, share in shares.items()
    }

    assert given["Reno"] == Decimal("300.00")
    assert given["Ellie's Savings"] == Decimal("100.00")
    # Equal weights are the old behaviour, so nothing changes for anyone who
    # never sets a share.
    assert round_down_to(remaining * Decimal(1) / Decimal(2)) == Decimal("200.00")
