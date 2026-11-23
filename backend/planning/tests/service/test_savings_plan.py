"""The savings plan engine, on hand-built balance paths.

Baselines are injected, so these pin the plan's own rules — what replaces
what, when a goal stops funding, where freed money goes, and what counts as
ideal, workable or insolvent — independently of the forecast machinery.
"""

from datetime import date, timedelta
from decimal import Decimal as D

import pytest

from planning.services.savings_plan import (
    INSOLVENT,
    IDEAL,
    WORKABLE,
    Baseline,
    PlanEntry,
    Window,
    _segments,
    find_dips,
    simulate,
)

TODAY = date(2026, 12, 1)
START = date(2027, 1, 1)
PAYDAYS = [START + timedelta(days=14 * i) for i in range(6)]  # Jan 1 .. Mar 12
END = date(2027, 3, 31)
FUNDING, A, B = 1, 10, 20


def window():
    return Window(start=START, end=END, paydays=PAYDAYS, options=PAYDAYS, horizon=END)


def funding(opening="10000", extra=()):
    rows = [(p, D("2000"), None) for p in PAYDAYS] + list(extra)
    return Baseline(FUNDING, D(opening), sorted(rows, key=lambda r: r[0]))


def account(account_id, opening="0", rows=()):
    return Baseline(account_id, D(opening), sorted(rows, key=lambda r: r[0]))


def run(entries, baselines, overrides=None):
    return simulate(
        TODAY, window(), entries, overrides, baselines=baselines, funding_id=FUNDING
    )


def entry(key, account_id, per, goal=None, goal_date=None, managed=()):
    e = PlanEntry(key=key, name=key, account_id=account_id, per_paycheck=D(per),
                  goal_amount=D(goal) if goal else None, goal_date=goal_date)
    e.managed = set(managed)
    return e


def bucket(plan, key):
    return next(b for b in plan["buckets"] if b["key"] == key)


@pytest.mark.django_db
def test_planned_amount_replaces_scheduled_transfers_from_the_window_on():
    # Reminder 7 funds A with 100: once in December (kept) and on every payday
    # in the window (replaced by the plan's 250).
    dec = date(2026, 12, 18)
    rows_a = [(dec, D("100"), 7)] + [(p, D("100"), 7) for p in PAYDAYS]
    rows_f = [(dec, D("-100"), 7)] + [(p, D("-100"), 7) for p in PAYDAYS]
    plan = run(
        [entry("a", A, "250", managed={7})],
        {FUNDING: funding(extra=rows_f), A: account(A, rows=rows_a)},
    )
    a = bucket(plan, "a")
    assert a["end_balance"] == D("100") + 6 * D("250")
    assert a["segments"] == [
        {"start": PAYDAYS[0], "end": PAYDAYS[-1], "amount": D("250.00"), "count": 6}
    ]
    assert a["changed"] is True
    # Funding: 10000 + 6*2000 income, -100 in December, -6*250 planned.
    assert plan["funding"]["end_balance"] == D("10000") + 6 * D("2000") - 100 - 6 * 250


@pytest.mark.django_db
def test_a_transfer_the_day_after_payday_is_that_paychecks_transfer():
    # Existing reminders land the day after payday; the plan lands on payday.
    # Same amount per paycheck, so nothing has changed.
    rows_a = [(p + timedelta(days=1), D("100"), 7) for p in PAYDAYS]
    plan = run(
        [entry("a", A, "100", managed={7})],
        {FUNDING: funding(), A: account(A, rows=rows_a)},
    )
    a = bucket(plan, "a")
    assert a["changed"] is False
    assert a["segments"][0]["start"] == PAYDAYS[0]
    plan = run(
        [entry("a", A, "120", managed={7})],
        {FUNDING: funding(), A: account(A, rows=rows_a)},
    )
    assert bucket(plan, "a")["changed"] is True


@pytest.mark.django_db
def test_restating_the_scheduled_amount_is_not_a_change():
    rows_a = [(p, D("100"), 7) for p in PAYDAYS]
    plan = run(
        [entry("a", A, "100", managed={7})],
        {FUNDING: funding(), A: account(A, rows=rows_a)},
    )
    assert bucket(plan, "a")["changed"] is False


@pytest.mark.django_db
def test_nothing_below_zero_is_ideal():
    plan = run([entry("a", A, "100")], {FUNDING: funding(), A: account(A, "50")})
    assert plan["verdict"] == IDEAL
    assert bucket(plan, "a")["verdict"] == IDEAL


@pytest.mark.django_db
def test_a_dip_the_next_paycheck_clears_is_workable():
    # A bill of 150 lands the day after the first transfer of 100.
    bill = [(PAYDAYS[0] + timedelta(days=1), D("-150"), None)]
    plan = run([entry("a", A, "100")], {FUNDING: funding(), A: account(A, "0", bill)})
    a = bucket(plan, "a")
    assert a["verdict"] == WORKABLE
    assert a["dips"][0]["paydays_below"] == 1
    assert plan["verdict"] == WORKABLE


@pytest.mark.django_db
def test_a_dip_across_two_paychecks_is_insolvent():
    bill = [(PAYDAYS[0] + timedelta(days=1), D("-250"), None)]
    plan = run([entry("a", A, "100")], {FUNDING: funding(), A: account(A, "0", bill)})
    assert bucket(plan, "a")["verdict"] == INSOLVENT
    assert plan["verdict"] == INSOLVENT


@pytest.mark.django_db
def test_the_funding_account_may_not_dip_even_for_a_day():
    bill = [(PAYDAYS[1] + timedelta(days=1), D("-1950"), None)]
    plan = run(
        [entry("a", A, "100")],
        {FUNDING: funding(opening="0", extra=bill), A: account(A, "0")},
    )
    # 2000 - 100 = 1900 after payday 1; +2000 -100 = 3800 after payday 2, so
    # -1950 is fine. Now make it tight: it is the *first* payday.
    assert plan["funding"]["verdict"] == IDEAL
    bill = [(PAYDAYS[0] + timedelta(days=1), D("-1950"), None)]
    plan = run(
        [entry("a", A, "100")],
        {FUNDING: funding(opening="0", extra=bill), A: account(A, "0")},
    )
    assert plan["funding"]["verdict"] == INSOLVENT
    assert plan["verdict"] == INSOLVENT


@pytest.mark.django_db
def test_reaching_a_goal_warns_but_the_plan_keeps_funding():
    # A starts at 150 and wants 400 at 100 a paycheck: 250, 350, 450 — the
    # goal is reached on the third transfer. The plan stands until a review,
    # so the transfers carry on, and the warning says what that costs.
    plan = run(
        [entry("a", A, "100", goal="400"), entry("b", B, "50", goal="100000")],
        {FUNDING: funding(), A: account(A, "150"), B: account(B, "0")},
    )
    a, b = bucket(plan, "a"), bucket(plan, "b")
    assert a["goal_reached_on"] == PAYDAYS[2]
    assert a["segments"] == [
        {"start": PAYDAYS[0], "end": PAYDAYS[-1], "amount": D("100.00"), "count": 6}
    ]
    assert a["paid_after_goal"] == D("300")
    assert a["end_balance"] == D("750")
    # Nothing is reallocated: B gets exactly its own 50.
    assert [s["amount"] for s in b["segments"]] == [D("50")]
    assert b["goal_reached_on"] is None and b["shortfall"] > 0
    # Short of a goal is flagged, never a failure.
    assert plan["verdict"] == IDEAL
    assert "unallocated" not in plan


@pytest.mark.django_db
def test_removed_buckets_stop_being_funded():
    rows_f = [(p, D("-100"), 7) for p in PAYDAYS]
    e = entry("a", A, "100", managed={7})
    e.remove = True
    plan = run([e], {FUNDING: funding(extra=rows_f), A: account(A)})
    assert bucket(plan, "a")["removed"] is True
    assert plan["funding"]["end_balance"] == D("10000") + 6 * D("2000")


@pytest.mark.django_db
def test_new_buckets_are_simulated_like_any_other():
    e = entry("new0", A, "75", goal="300")
    plan = run([e], {FUNDING: funding(), A: account(A)})
    assert bucket(plan, "new0")["goal_reached_on"] == PAYDAYS[3]


@pytest.mark.django_db
def test_suggested_rules_carry_each_shortfall():
    plan = run(
        [entry("a", A, "10", goal="1000"), entry("b", B, "10", goal="5")],
        {FUNDING: funding(), A: account(A), B: account(B)},
        overrides=["b", "a"],
    )
    assert [r["key"] for r in plan["suggested_rules"]] == ["b", "a"]
    gaps = {r["key"]: r["shortfall"] for r in plan["suggested_rules"]}
    assert gaps["a"] == D("1000") - 6 * D("10")
    assert gaps["b"] == D("0")
    assert all(r["cap_amount"] is None for r in plan["suggested_rules"])


@pytest.mark.unit
def test_find_dips_counts_paydays_survived_not_the_opening_one():
    points = [
        (date(2027, 1, 1), D("-5")),
        (date(2027, 1, 15), D("-1")),
        (date(2027, 1, 16), D("10")),
    ]
    dips = find_dips(points, [date(2027, 1, 1), date(2027, 1, 15), date(2027, 1, 29)])
    assert len(dips) == 1
    assert dips[0].paydays_below == 1
    assert dips[0].tolerable


@pytest.mark.unit
def test_a_dip_that_never_recovers_is_never_tolerable():
    dips = find_dips([(date(2027, 1, 1), D("-5"))], [date(2027, 1, 1)])
    assert dips[0].recovers_on is None
    assert not dips[0].tolerable


@pytest.mark.unit
def test_segments_collapse_runs():
    d = [date(2027, 1, 1) + timedelta(days=14 * i) for i in range(4)]
    runs = _segments([(d[0], D("1")), (d[1], D("1")), (d[2], D("0")), (d[3], D("0"))])
    assert [(r["amount"], r["count"]) for r in runs] == [(D("1"), 2), (D("0"), 2)]


@pytest.mark.unit
def test_the_windows_last_day_is_in_the_forecast(monkeypatch):
    # The forecast's end date is exclusive. Asking it for "through Dec 31"
    # with end=Dec 31 dropped the Dec 31 paycheck while the plan still paid
    # that paycheck's transfers, sending checking 2,700 negative on paper.
    from planning.services import savings_plan as sp

    asked = {}

    def fake(end_date, account_id, totals_only, forecast, start_date, cleared_only):
        asked["end"] = end_date
        return [], D("0")

    monkeypatch.setattr(sp, "get_account_transactions_and_balances", fake)
    sp._compute_baseline(FUNDING, TODAY, date(2027, 12, 31))
    assert asked["end"] == date(2028, 1, 1)
