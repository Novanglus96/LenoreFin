"""Income reminders measured against what actually arrived.

Capacity is built from the reminders, so a stale one makes every figure in the
plan wrong in the same direction — and silently, because the plan just reports
a smaller household than the one that exists. On real data a payroll reminder
was 251.73 a payday light, 6,567.46 a year, which is the same order as the
shortfall the plan was reporting at the time.
"""

from datetime import timedelta
from decimal import Decimal

import pytest

from planning.services.income_review import MIN_DEPOSITS, review_income


def deposited(description, amounts, status, ttype, start_days_ago=360):
    from transactions.models import Transaction
    from utils.dates import get_todays_date_timezone_adjusted

    today = get_todays_date_timezone_adjusted()
    for i, amount in enumerate(amounts):
        Transaction.objects.create(
            transaction_date=today - timedelta(days=start_days_ago - i * 14),
            total_amount=Decimal(str(amount)),
            description=description,
            transaction_type=ttype,
            status=status,
        )


@pytest.fixture
def cleared(db):
    from transactions.models import TransactionStatus

    status, _ = TransactionStatus.objects.get_or_create(
        transaction_status="Cleared", defaults={"slug": "cleared"}
    )
    return status


@pytest.fixture
def income_type(db):
    from transactions.models import TransactionType

    ttype, _ = TransactionType.objects.get_or_create(
        transaction_type="Income", defaults={"slug": "income"}
    )
    return ttype


@pytest.fixture
def payroll(test_checking_account, test_repeat, test_tag, income_type):
    from reminders.models import Reminder

    return Reminder.objects.create(
        tag=test_tag,
        amount=Decimal("1000.00"),
        reminder_source_account=test_checking_account,
        description="Payroll",
        transaction_type=income_type,
        repeat=test_repeat,
    )


@pytest.mark.service
@pytest.mark.django_db
def test_a_stale_reminder_is_reported(
    payroll, cleared, income_type, test_checking_account,
):
    from utils.dates import get_todays_date_timezone_adjusted

    deposited("Payroll", [1250] * 10, cleared, income_type)

    review = review_income(
        get_todays_date_timezone_adjusted(), test_checking_account.id
    )

    assert len(review.drifts) == 1
    drift = review.drifts[0]
    assert drift.median_amount == Decimal("1250.00")
    assert drift.drift == Decimal("250.00")


@pytest.mark.service
@pytest.mark.django_db
def test_the_median_is_offered_and_the_overtime_is_only_reported(
    payroll, cleared, income_type, test_checking_account,
):
    """A plan that depends on overtime is not a plan.

    Eight ordinary checks and two big ones. The figure to put in the reminder
    is what a typical payday brings, not what the good months averaged — the
    difference between the two is exactly the money not to count on.
    """
    from utils.dates import get_todays_date_timezone_adjusted

    deposited("Payroll", [1250] * 8 + [2600, 2800], cleared, income_type)

    drift = review_income(
        get_todays_date_timezone_adjusted(), test_checking_account.id
    ).drifts[0]

    assert drift.median_amount == Decimal("1250.00")
    assert drift.mean_amount > drift.median_amount
    assert drift.upside_per_deposit == drift.mean_amount - drift.median_amount
    assert "not worth planning on" in drift.why


@pytest.mark.service
@pytest.mark.django_db
def test_a_small_difference_is_not_reported(
    payroll, cleared, income_type, test_checking_account,
):
    """4% on a paycheck is payroll rounding, not a raise."""
    from utils.dates import get_todays_date_timezone_adjusted

    deposited("Payroll", [1040] * 10, cleared, income_type)

    assert review_income(
        get_todays_date_timezone_adjusted(), test_checking_account.id
    ).drifts == []


@pytest.mark.service
@pytest.mark.django_db
def test_too_few_deposits_is_an_anecdote_not_a_measurement(
    payroll, cleared, income_type, test_checking_account,
):
    from utils.dates import get_todays_date_timezone_adjusted

    deposited("Payroll", [1500] * (MIN_DEPOSITS - 1), cleared, income_type)

    assert review_income(
        get_todays_date_timezone_adjusted(), test_checking_account.id
    ).drifts == []
