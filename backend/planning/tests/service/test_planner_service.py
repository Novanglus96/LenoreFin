"""Tests for the trend analysis the savings planner measures accounts with.

The arithmetic here is the whole feature, so the numbers are checked against
figures worked out by hand rather than against whatever the code happens to
return. `today` is injected everywhere — a module-level date literal compared
against the real clock is a time bomb, and this repo has been bitten by one.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from planning.models import Bucket
from planning.services.planner import (
    analyze_account_trend,
    paychecks_per_year,
)
from reminders.models import Repeat
from transactions.models import Transaction

TODAY = date(2026, 8, 26)


def _tx(account, amount, when, status, ttype, source=None, destination=None):
    return Transaction.objects.create(
        transaction_date=when,
        total_amount=Decimal(str(amount)),
        status=status,
        description="Test",
        transaction_type=ttype,
        source_account=source,
        destination_account=destination,
    )


@pytest.fixture
def biweekly_repeat():
    return Repeat.objects.create(
        repeat_name="Every 2 Weeks", days=0, weeks=2, months=0, years=0
    )


@pytest.fixture
def draining_account(
    test_savings_account,
    test_cleared_transaction_status,
    test_expense_transaction_type,
):
    """A savings account bleeding exactly 100.00 a month for six months.

    Opening 55.55 + archive 555.55 = 611.10, then six monthly 100.00 expenses.
    """
    for i in range(6):
        _tx(
            test_savings_account,
            -100,
            TODAY - timedelta(days=30 * (i + 1)),
            test_cleared_transaction_status,
            test_expense_transaction_type,
            source=test_savings_account,
        )
    return test_savings_account


@pytest.mark.service
@pytest.mark.django_db
def test_trend_measures_natural_drain(draining_account):
    trend = analyze_account_trend(draining_account.id, months=6, today=TODAY)

    assert trend is not None
    assert trend.data_points == 6
    # Six 100.00 expenses over a ~6 month window.
    assert trend.natural_flow_per_month < Decimal("0")
    assert trend.natural_flow_per_month == pytest.approx(
        Decimal("-101.46"), abs=Decimal("0.05")
    )
    # 611.10 opening less 600 spent.
    assert trend.current_balance == Decimal("11.10")


@pytest.mark.service
@pytest.mark.django_db
def test_trend_excludes_bucket_transfers(
    draining_account,
    test_checking_account,
    test_cleared_transaction_status,
    test_transfer_transaction_type,
):
    """Top-ups from the funding account must not mask the drain.

    This is the whole point of the exclusion: without it an account that is
    bleeding 100/month but being topped up 100/month looks perfectly healthy,
    and the planner would suggest changing nothing.
    """
    for i in range(6):
        _tx(
            draining_account,
            100,
            TODAY - timedelta(days=30 * (i + 1) - 1),
            test_cleared_transaction_status,
            test_transfer_transaction_type,
            source=test_checking_account,
            destination=draining_account,
        )

    trend = analyze_account_trend(
        draining_account.id,
        months=6,
        source_account_id=test_checking_account.id,
        today=TODAY,
    )

    assert trend is not None
    # The balance is flat, but the natural flow is still the full drain.
    assert trend.current_balance == Decimal("611.10")
    assert trend.natural_flow_per_month == pytest.approx(
        Decimal("-101.46"), abs=Decimal("0.05")
    )
    assert trend.excluded_contribution_total == Decimal("600.00")


@pytest.mark.service
@pytest.mark.django_db
def test_insufficient_history_returns_no_trend(
    test_savings_account,
    test_cleared_transaction_status,
    test_expense_transaction_type,
):
    _tx(
        test_savings_account,
        -10,
        TODAY - timedelta(days=5),
        test_cleared_transaction_status,
        test_expense_transaction_type,
        source=test_savings_account,
    )

    assert analyze_account_trend(test_savings_account.id, months=6, today=TODAY) is None


@pytest.mark.service
@pytest.mark.django_db
def test_paychecks_per_year_derives_from_repeat(
    draining_account, test_checking_account, biweekly_repeat,
    test_transfer_transaction_type,
):
    from reminders.models import Reminder

    reminder = Reminder.objects.create(
        amount=Decimal("100.00"),
        reminder_source_account=test_checking_account,
        reminder_destination_account=draining_account,
        description="Biweekly",
        transaction_type=test_transfer_transaction_type,
        repeat=biweekly_repeat,
    )
    bucket = Bucket.objects.create(
        name="Cadence",
        contribution_per_paycheck=Decimal("100.00"),
        account=draining_account,
        reminder=reminder,
    )

    assert paychecks_per_year(bucket) == pytest.approx(
        Decimal("26.09"), abs=Decimal("0.1")
    )


@pytest.mark.service
@pytest.mark.django_db
def test_paychecks_per_year_falls_back_to_biweekly(draining_account):
    """An unlinked bucket still solves, on the common-case cadence."""
    bucket = Bucket.objects.create(
        name="NoLink",
        contribution_per_paycheck=Decimal("100.00"),
        account=draining_account,
    )

    assert paychecks_per_year(bucket) == Decimal("26")


@pytest.mark.service
@pytest.mark.django_db
def test_one_off_spending_is_not_projected_as_a_rate(
    test_savings_account, test_cleared_transaction_status,
    test_expense_transaction_type,
):
    """A single large expense is an event, not a monthly burn.

    Found against real data: one bucket's entire unscheduled history was
    "Closing Costs" and "Home Transfer", once each. Treating 5,654 of
    house-purchase costs as a recurring rate asked for an extra 573 a paycheck,
    forever.
    """
    _tx(test_savings_account, -3500, TODAY - timedelta(days=40),
        test_cleared_transaction_status, test_expense_transaction_type,
        source=test_savings_account)
    one_off = Transaction.objects.get(total_amount=Decimal("-3500"))
    one_off.description = "Closing Costs"
    one_off.save(update_fields=["description"])
    # Two more, distinct one-offs — still events, not a rate.
    for i, (amt, desc) in enumerate([(-800, "Home Transfer"), (-450, "Survey")]):
        t = _tx(test_savings_account, amt, TODAY - timedelta(days=60 + i * 10),
                test_cleared_transaction_status, test_expense_transaction_type,
                source=test_savings_account)
        t.description = desc
        t.save(update_fields=["description"])

    trend = analyze_account_trend(test_savings_account.id, months=6, today=TODAY)

    assert trend is not None
    # Nothing recurs, so there is no ad-hoc rate at all.
    assert trend.adhoc_flow_per_month == Decimal("0.00")
    assert trend.one_off_total == Decimal("-4750.00")


@pytest.mark.service
@pytest.mark.django_db
def test_repeated_unscheduled_spending_is_a_rate(
    test_savings_account, test_cleared_transaction_status,
    test_expense_transaction_type,
):
    """Spending that recurs under one name is real, even with no reminder.

    The grocery bucket has no outflow reminder at all — its whole drain is
    repeated "Groceries Transfer" rows. A forecast-only planner would say it
    never spends anything and suggest cutting the bucket to zero.
    """
    for i in range(6):
        t = _tx(test_savings_account, -300, TODAY - timedelta(days=30 * (i + 1)),
                test_cleared_transaction_status, test_expense_transaction_type,
                source=test_savings_account)
        t.description = "Groceries Transfer"
        t.save(update_fields=["description"])

    trend = analyze_account_trend(test_savings_account.id, months=6, today=TODAY)

    assert trend is not None
    assert trend.one_off_total == Decimal("0.00")
    # 1800 over 5.9138 months.
    assert trend.adhoc_flow_per_month == pytest.approx(
        Decimal("-304.37"), abs=Decimal("0.05")
    )


@pytest.mark.service
@pytest.mark.django_db
def test_suggested_floor_sizes_the_excess_of_a_bad_month(
    test_savings_account, test_cleared_transaction_status,
    test_expense_transaction_type,
):
    """The buffer absorbs *variation*, not a whole month's spend.

    Sizing it to the worst month outright demanded that a pass-through grocery
    bucket hold a full month of spending idle.
    """
    # Five months of 300, one of 900. Worst is 900, average 400 → excess 500.
    for i, amt in enumerate([300, 300, 300, 300, 300, 900]):
        t = _tx(test_savings_account, -amt, TODAY - timedelta(days=30 * (i + 1) - 5),
                test_cleared_transaction_status, test_expense_transaction_type,
                source=test_savings_account)
        t.description = "Groceries Transfer"
        t.save(update_fields=["description"])

    trend = analyze_account_trend(test_savings_account.id, months=6, today=TODAY)

    assert trend.suggested_floor == pytest.approx(
        Decimal("500.00"), abs=Decimal("1")
    )


@pytest.mark.service
@pytest.mark.django_db
def test_a_single_transfer_is_not_treated_as_a_repeating_amount(
    draining_account, test_checking_account, biweekly_repeat,
    test_cleared_transaction_status, test_transfer_transaction_type,
):
    """With no repetition there is nothing to separate schedule from top-up."""
    t = _tx(draining_account, 200, TODAY - timedelta(days=20),
            test_cleared_transaction_status, test_transfer_transaction_type,
            source=test_checking_account, destination=draining_account)
    t.description = "Transfer to Reno"
    t.save(update_fields=["description"])

    trend = analyze_account_trend(
        draining_account.id, months=6,
        source_account_id=test_checking_account.id,
        contribution_description="Transfer to Reno",
        today=TODAY,
    )

    assert trend.modal_contribution_amount is None
    # Falls back to treating it as the bucket rather than inventing a split.
    assert trend.excluded_contribution_total == Decimal("200.00")
    assert trend.extra_contributions_total == Decimal("0.00")


@pytest.mark.service
@pytest.mark.django_db
def test_topups_are_measured_as_current_funding(
    test_savings_account, test_checking_account, biweekly_repeat,
    test_cleared_transaction_status, test_transfer_transaction_type,
):
    """Hand top-ups are funding that is already happening, and must be counted.

    Not projected — see the ad-hoc rate for why — but a baseline that ignores
    them treats money already going in as money still to be found. On real data
    that was 694 a paycheck, and it produced a shortfall the account balances
    flatly contradicted.
    """
    # 13 scheduled transfers at 75, plus three top-ups sharing the description.
    for i in range(13):
        _tx(test_savings_account, 75, TODAY - timedelta(days=14 * (i + 1)),
            test_cleared_transaction_status, test_transfer_transaction_type,
            source=test_checking_account, destination=test_savings_account)
    for extra in (850, 510, 1000):
        _tx(test_savings_account, extra, TODAY - timedelta(days=40),
            test_cleared_transaction_status, test_transfer_transaction_type,
            source=test_checking_account, destination=test_savings_account)

    trend = analyze_account_trend(
        test_savings_account.id,
        months=6,
        source_account_id=test_checking_account.id,
        today=TODAY,
        contribution_description="Test",
    )

    assert trend is not None
    # The modal amount is the bucket; the rest is extra.
    assert trend.modal_contribution_amount == Decimal("75.00")
    assert trend.extra_contributions_total == Decimal("2360.00")
    # 2360 over the 12.81 paychecks in a 180-day window.
    assert trend.topup_per_paycheck == pytest.approx(
        Decimal("184.20"), abs=Decimal("0.5")
    )