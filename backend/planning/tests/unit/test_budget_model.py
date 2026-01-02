import pytest
from planning.models import Budget
from reminders.models import Repeat
from django.utils import timezone
import pytz
import os
from django.db import IntegrityError


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.mark.django_db
def test_budget_creation():
    repeat = Repeat.objects.create(repeat_name="Test")

    budget = Budget.objects.create(
        tag_ids="tag ids",
        name="Test Budget",
        amount=0.00,
        roll_over=True,
        repeat=repeat,
        start_day=current_date(),
        roll_over_amt=0.00,
        active=True,
        widget=True,
        next_start=current_date(),
    )

    assert budget.id is not None
    assert budget.tag_ids == "tag ids"
    assert budget.name == "Test Budget"
    assert budget.amount == 0.00
    assert budget.roll_over
    assert budget.repeat == repeat
    assert budget.start_day == current_date()
    assert budget.roll_over_amt == 0.00
    assert budget.active
    assert budget.widget
    assert budget.next_start == current_date()


@pytest.mark.django_db
def test_budget_defaults():
    budget = Budget.objects.create(
        tag_ids="tag ids",
        name="Test Budget",
    )

    assert budget.id is not None
    assert budget.amount == 0.00
    assert budget.roll_over
    assert budget.repeat is None
    assert budget.start_day == current_date()
    assert budget.roll_over_amt == 0.00
    assert budget.active
    assert budget.widget
    assert budget.next_start == current_date()


@pytest.mark.django_db
def test_name_uniqueness():
    Budget.objects.create(
        tag_ids="tag ids",
        name="Test Budget",
    )

    with pytest.raises(IntegrityError):
        Budget.objects.create(
            tag_ids="tag ids",
            name="Test Budget",
        )


@pytest.mark.django_db
def test_budget_string_representation():
    budget = Budget.objects.create(
        tag_ids="tag ids",
        name="Test Budget",
    )
    expected = "Test Budget"

    assert str(budget) == expected
