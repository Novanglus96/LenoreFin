"""Tests for the financial planner's trend analysis and goal solvers.

The arithmetic here is the whole feature, so the numbers are checked against
figures worked out by hand rather than against whatever the code happens to
return. `today` is injected everywhere — a module-level date literal compared
against the real clock is a time bomb, and this repo has been bitten by one.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from planning.models import Contribution
from planning.services.planner import (
    analyze_account_trend,
    analyze_contribution,
    paychecks_per_year,
    project_with_contribution,
    solve_for_contribution,
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
def test_trend_excludes_contribution_transfers(
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
def test_hold_goal_offsets_the_drift(
    draining_account, test_checking_account, biweekly_repeat,
    test_transfer_transaction_type,
):
    """The headline case: account trending down, goal is flat, solve the top-up.

    -101.46/month over 26.09 paychecks a year is -46.67 a paycheck, so holding
    flat needs exactly that much added each payday.
    """
    from reminders.models import Reminder

    reminder = Reminder.objects.create(
        amount=Decimal("10.00"),
        reminder_source_account=test_checking_account,
        reminder_destination_account=draining_account,
        description="House Transfer",
        transaction_type=test_transfer_transaction_type,
        repeat=biweekly_repeat,
    )
    contribution = Contribution.objects.create(
        contribution="House",
        per_paycheck=Decimal("10.00"),
        account=draining_account,
        reminder=reminder,
        goal_type=Contribution.GOAL_HOLD,
    )

    trend = analyze_account_trend(draining_account.id, months=6, today=TODAY)
    suggestion = solve_for_contribution(contribution, trend, today=TODAY)

    assert suggestion is not None
    assert suggestion.paychecks_per_year == pytest.approx(
        Decimal("26.09"), abs=Decimal("0.1")
    )
    assert suggestion.required_per_paycheck == pytest.approx(
        Decimal("46.67"), abs=Decimal("0.05")
    )
    # Currently contributing 10, so the shortfall is the rest.
    assert suggestion.delta_per_paycheck == pytest.approx(
        Decimal("36.67"), abs=Decimal("0.05")
    )


@pytest.mark.service
@pytest.mark.django_db
def test_target_goal_covers_gap_and_drift(
    draining_account, test_checking_account, biweekly_repeat,
    test_transfer_transaction_type,
):
    """A target must fund the gap *and* offset the drain along the way."""
    from reminders.models import Reminder

    reminder = Reminder.objects.create(
        amount=Decimal("0.00"),
        reminder_source_account=test_checking_account,
        reminder_destination_account=draining_account,
        description="Kids",
        transaction_type=test_transfer_transaction_type,
        repeat=biweekly_repeat,
    )
    contribution = Contribution.objects.create(
        contribution="Kids",
        per_paycheck=Decimal("0.00"),
        account=draining_account,
        reminder=reminder,
        goal_type=Contribution.GOAL_TARGET,
        goal_amount=Decimal("5000.00"),
        goal_date=TODAY + timedelta(days=365),
    )

    trend = analyze_account_trend(draining_account.id, months=6, today=TODAY)
    suggestion = solve_for_contribution(contribution, trend, today=TODAY)

    assert suggestion is not None
    assert suggestion.achievable
    # Gap is 4988.90 over 26.07 paychecks (191.36), plus 46.67 of drift.
    assert suggestion.required_per_paycheck == pytest.approx(
        Decimal("238.03"), abs=Decimal("0.1")
    )


@pytest.mark.service
@pytest.mark.django_db
def test_target_goal_in_the_past_is_not_achievable(
    draining_account, biweekly_repeat,
):
    contribution = Contribution.objects.create(
        contribution="Late",
        per_paycheck=Decimal("25.00"),
        account=draining_account,
        goal_type=Contribution.GOAL_TARGET,
        goal_amount=Decimal("1000.00"),
        goal_date=TODAY - timedelta(days=1),
    )

    trend = analyze_account_trend(draining_account.id, months=6, today=TODAY)
    suggestion = solve_for_contribution(contribution, trend, today=TODAY)

    assert suggestion is not None
    assert suggestion.achievable is False
    assert suggestion.delta_per_paycheck == Decimal("0")


@pytest.mark.service
@pytest.mark.django_db
def test_grow_goal_by_amount(draining_account, biweekly_repeat):
    """Growth stacks on top of offsetting the drift, not instead of it."""
    contribution = Contribution.objects.create(
        contribution="Grow",
        per_paycheck=Decimal("0.00"),
        account=draining_account,
        goal_type=Contribution.GOAL_GROW,
        goal_amount=Decimal("50.00"),
    )

    trend = analyze_account_trend(draining_account.id, months=6, today=TODAY)
    suggestion = solve_for_contribution(contribution, trend, today=TODAY)

    assert suggestion is not None
    # No reminder is linked, so the cadence falls back to 26 paychecks:
    # 46.83 to hold flat, plus 50/month (23.08 a paycheck) to grow.
    assert suggestion.required_per_paycheck == pytest.approx(
        Decimal("69.90"), abs=Decimal("0.05")
    )


@pytest.mark.service
@pytest.mark.django_db
def test_floor_goal_suggests_no_change_when_comfortably_above(
    test_savings_account,
    test_cleared_transaction_status,
    test_income_transaction_type,
):
    """An account already climbing past its floor needs no extra money."""
    for i in range(4):
        _tx(
            test_savings_account,
            500,
            TODAY - timedelta(days=30 * (i + 1)),
            test_cleared_transaction_status,
            test_income_transaction_type,
            destination=test_savings_account,
        )
    contribution = Contribution.objects.create(
        contribution="Floor",
        per_paycheck=Decimal("20.00"),
        account=test_savings_account,
        goal_type=Contribution.GOAL_FLOOR,
        goal_amount=Decimal("100.00"),
    )

    trend = analyze_account_trend(test_savings_account.id, months=6, today=TODAY)
    suggestion = solve_for_contribution(contribution, trend, today=TODAY)

    assert suggestion is not None
    assert suggestion.delta_per_paycheck == Decimal("0")
    assert "above" in suggestion.reason


@pytest.mark.service
@pytest.mark.django_db
def test_self_funding_account_floors_requirement_at_zero(
    test_savings_account,
    test_cleared_transaction_status,
    test_income_transaction_type,
):
    """A negative requirement is reported as zero plus a warning, not a negative transfer."""
    for i in range(6):
        _tx(
            test_savings_account,
            300,
            TODAY - timedelta(days=30 * (i + 1)),
            test_cleared_transaction_status,
            test_income_transaction_type,
            destination=test_savings_account,
        )
    contribution = Contribution.objects.create(
        contribution="SelfFund",
        per_paycheck=Decimal("50.00"),
        account=test_savings_account,
        goal_type=Contribution.GOAL_HOLD,
    )

    trend = analyze_account_trend(test_savings_account.id, months=6, today=TODAY)
    suggestion = solve_for_contribution(contribution, trend, today=TODAY)

    assert suggestion is not None
    assert suggestion.required_per_paycheck == Decimal("0.00")
    assert suggestion.warning is not None
    assert "grows on its own" in suggestion.warning


@pytest.mark.service
@pytest.mark.django_db
def test_no_goal_yields_no_suggestion(draining_account):
    contribution = Contribution.objects.create(
        contribution="Plain",
        per_paycheck=Decimal("10.00"),
        account=draining_account,
        goal_type=Contribution.GOAL_NONE,
    )
    trend = analyze_account_trend(draining_account.id, months=6, today=TODAY)

    assert solve_for_contribution(contribution, trend, today=TODAY) is None


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
    contribution = Contribution.objects.create(
        contribution="Cadence",
        per_paycheck=Decimal("100.00"),
        account=draining_account,
        reminder=reminder,
    )

    assert paychecks_per_year(contribution) == pytest.approx(
        Decimal("26.09"), abs=Decimal("0.1")
    )


@pytest.mark.service
@pytest.mark.django_db
def test_paychecks_per_year_falls_back_to_biweekly(draining_account):
    """An unlinked contribution still solves, on the common-case cadence."""
    contribution = Contribution.objects.create(
        contribution="NoLink",
        per_paycheck=Decimal("100.00"),
        account=draining_account,
    )

    assert paychecks_per_year(contribution) == Decimal("26")


@pytest.mark.service
@pytest.mark.django_db
def test_drift_reports_gap_between_plan_and_schedule(
    draining_account, test_checking_account, biweekly_repeat,
    test_transfer_transaction_type,
):
    """The plan says 200, the reminder moves 150 — that gap must surface."""
    from reminders.models import Reminder

    reminder = Reminder.objects.create(
        amount=Decimal("150.00"),
        reminder_source_account=test_checking_account,
        reminder_destination_account=draining_account,
        description="Drifted",
        transaction_type=test_transfer_transaction_type,
        repeat=biweekly_repeat,
    )
    contribution = Contribution.objects.create(
        contribution="Drift",
        per_paycheck=Decimal("200.00"),
        account=draining_account,
        reminder=reminder,
        goal_type=Contribution.GOAL_HOLD,
    )

    result = analyze_contribution(contribution, months=6, today=TODAY)

    assert result is not None
    assert result["drift"] == Decimal("50.00")


@pytest.mark.service
@pytest.mark.django_db
def test_drift_is_none_without_a_reminder(draining_account):
    """No reminder means no comparison — which is not the same as no drift."""
    contribution = Contribution.objects.create(
        contribution="Unlinked",
        per_paycheck=Decimal("200.00"),
        account=draining_account,
        goal_type=Contribution.GOAL_HOLD,
    )

    result = analyze_contribution(contribution, months=6, today=TODAY)

    assert result is not None
    assert result["drift"] is None


@pytest.mark.service
@pytest.mark.django_db
def test_analyze_contribution_without_account_returns_none():
    contribution = Contribution.objects.create(
        contribution="Orphan", per_paycheck=Decimal("10.00")
    )

    assert analyze_contribution(contribution, months=6, today=TODAY) is None


@pytest.mark.service
@pytest.mark.django_db
def test_projection_curves_diverge_by_the_delta(draining_account):
    """The suggested curve must beat the current one by exactly the delta."""
    contribution = Contribution.objects.create(
        contribution="Proj",
        per_paycheck=Decimal("10.00"),
        account=draining_account,
        goal_type=Contribution.GOAL_HOLD,
    )
    trend = analyze_account_trend(draining_account.id, months=6, today=TODAY)
    suggestion = solve_for_contribution(contribution, trend, today=TODAY)

    rows = project_with_contribution(trend, suggestion, months=12)

    assert len(rows) == 13
    assert rows[0][1] == rows[0][2] == trend.current_balance
    # Holding flat means the applied curve ends where it started.
    assert rows[-1][2] == pytest.approx(trend.current_balance, abs=Decimal("2"))
    # And it must be strictly better than doing nothing.
    assert rows[-1][2] > rows[-1][1]


@pytest.mark.service
@pytest.mark.django_db
def test_second_funding_stream_is_not_silently_excluded(
    draining_account, test_checking_account, biweekly_repeat,
    test_cleared_transaction_status, test_transfer_transaction_type,
):
    """Another transfer from the same source must not vanish from the maths.

    Found against real data: an account fed by two biweekly transfers from the
    same checking account had *both* excluded as "the contribution", so the
    second stream was dropped from natural flow without being credited back.
    The account looked like it drained twice as fast as it did and the
    suggestion came back roughly four times too large.

    Only the transfer matching the linked reminder's description is the
    contribution; anything else arriving is natural inflow.
    """
    from reminders.models import Reminder

    reminder = Reminder.objects.create(
        amount=Decimal("-100.00"),
        reminder_source_account=test_checking_account,
        reminder_destination_account=draining_account,
        description="Transfer to House",
        transaction_type=test_transfer_transaction_type,
        repeat=biweekly_repeat,
    )
    contribution = Contribution.objects.create(
        contribution="House",
        per_paycheck=Decimal("100.00"),
        account=draining_account,
        reminder=reminder,
        goal_type=Contribution.GOAL_HOLD,
    )
    # The contribution's own stream, named like the reminder.
    for i in range(6):
        _tx(draining_account, 100, TODAY - timedelta(days=30 * (i + 1) - 1),
            test_cleared_transaction_status, test_transfer_transaction_type,
            source=test_checking_account, destination=draining_account)
    # A separate stream from the same account, under a different name.
    for i in range(6):
        t = _tx(draining_account, 400, TODAY - timedelta(days=30 * (i + 1) - 2),
                test_cleared_transaction_status, test_transfer_transaction_type,
                source=test_checking_account, destination=draining_account)
        t.description = "DCA Transfer"
        t.save(update_fields=["description"])
    for t in Transaction.objects.filter(
        destination_account=draining_account, total_amount=Decimal("100")
    ):
        t.description = "Transfer to House"
        t.save(update_fields=["description"])

    trend = analyze_account_trend(
        draining_account.id, months=6,
        source_account_id=test_checking_account.id,
        contribution_description="Transfer to House",
        today=TODAY,
    )

    # Only the 6 x 100 stream is the contribution.
    assert trend.excluded_contribution_total == Decimal("600.00")
    # The 6 x 400 stream stays in natural flow, offsetting the 600 of spending:
    # (2400 - 600) / 5.9138 months.
    assert trend.natural_flow_per_month == pytest.approx(
        Decimal("304.37"), abs=Decimal("0.05")
    )

    suggestion = solve_for_contribution(contribution, trend, today=TODAY)
    # The account is funded well beyond its drain, so nothing more is needed.
    assert suggestion.required_per_paycheck == Decimal("0.00")
    assert suggestion.warning is not None
