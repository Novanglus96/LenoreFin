"""A budget that totals other budgets.

Budgets were flat and tag-based, so a household wanting a Christmas total had
to write a Christmas budget *and* a budget per person, over the same tags, with
nothing keeping the two in step. They drifted exactly as you would expect: the
parent said 1,995, the twenty-three children summed to 1,130, and the actual
spend was 2,177. Three numbers that should have been one.

A parent is now the sum of its children, and only a parent speaks.
"""

import json
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from planning.models import Budget
from planning.services.budget_math import (
    budget_tag_ids,
    spending_budgets,
)

pytestmark = [pytest.mark.service, pytest.mark.django_db]


@pytest.fixture
def yearly(db):
    from reminders.models import Repeat

    repeat, _ = Repeat.objects.get_or_create(
        repeat_name="Every Year", defaults={"years": 1, "slug": "every-year"}
    )
    return repeat


@pytest.fixture
def monthly(db):
    from reminders.models import Repeat

    repeat, _ = Repeat.objects.get_or_create(
        repeat_name="Every Month", defaults={"months": 1, "slug": "every-month"}
    )
    return repeat


def a_budget(name, amount, repeat, tags=(), parent=None):
    return Budget.objects.create(
        name=name,
        amount=Decimal(str(amount)),
        repeat=repeat,
        tag_ids=json.dumps(list(tags)),
        parent=parent,
        active=True,
    )


def test_a_parent_is_the_sum_of_its_children(yearly):
    christmas = a_budget("Christmas", 1995, yearly)
    a_budget("Christmas - John", 100, yearly, parent=christmas)
    a_budget("Christmas - Ellie", 150, yearly, parent=christmas)

    # The stored 1,995 is ignored: a parent exists to total its parts, not to
    # hold a figure that drifts away from them.
    assert christmas.planned_amount == Decimal("250.00")
    assert christmas.is_parent is True


def test_children_are_converted_into_the_parents_cadence(yearly, monthly):
    """A yearly total over monthly parts is a reasonable thing to want, and
    adding the face values would be out by a factor of twelve."""
    yearly_parent = a_budget("Household", 0, yearly)
    a_budget("Cleaning", 50, monthly, parent=yearly_parent)

    assert yearly_parent.planned_amount == Decimal("600.00")


def test_an_inactive_child_stops_counting(yearly):
    christmas = a_budget("Christmas", 0, yearly)
    a_budget("Christmas - John", 100, yearly, parent=christmas)
    retired = a_budget("Christmas - Old Colleague", 40, yearly, parent=christmas)

    retired.active = False
    retired.save()

    assert christmas.planned_amount == Decimal("100.00")


def test_a_leaf_still_reports_its_own_amount(yearly):
    groceries = a_budget("Groceries", 460, yearly)

    assert groceries.planned_amount == Decimal("460.00")
    assert groceries.is_parent is False


def test_a_parent_speaks_for_its_own_tags_and_its_childrens(yearly):
    """Kept, not replaced. A parent often covers ground no child claims —
    twenty-two tags against one apiece — and dropping the parent's own would
    silently stop funding whatever nobody wrote a line for."""
    christmas = a_budget("Christmas", 0, yearly, tags=[1, 2, 3])
    a_budget("Christmas - John", 100, yearly, tags=[3, 4], parent=christmas)

    assert budget_tag_ids(christmas) == [1, 2, 3, 4]


def test_only_parents_and_leaves_speak(yearly):
    """A child's spending is already inside its parent's total."""
    christmas = a_budget("Christmas", 0, yearly)
    a_budget("Christmas - John", 100, yearly, parent=christmas)
    groceries = a_budget("Groceries", 460, yearly)

    speaking = spending_budgets(Budget.objects.all())

    assert sorted(b.name for b in speaking) == ["Christmas", "Groceries"]
    assert groceries in speaking


def test_budgets_only_nest_one_level(yearly):
    christmas = a_budget("Christmas", 0, yearly)
    john = a_budget("Christmas - John", 100, yearly, parent=christmas)
    deeper = a_budget("Christmas - John - Socks", 10, yearly)

    deeper.parent = john
    with pytest.raises(ValidationError):
        deeper.full_clean(exclude=["tag_ids", "name"])


def test_a_budget_that_totals_others_cannot_join_a_total(yearly):
    christmas = a_budget("Christmas", 0, yearly)
    a_budget("Christmas - John", 100, yearly, parent=christmas)
    other = a_budget("Gifts", 500, yearly)

    christmas.parent = other
    with pytest.raises(ValidationError):
        christmas.full_clean(exclude=["tag_ids", "name"])


def test_a_budget_cannot_be_its_own_total(yearly):
    christmas = a_budget("Christmas", 0, yearly)

    christmas.parent = christmas
    with pytest.raises(ValidationError):
        christmas.full_clean(exclude=["tag_ids", "name"])


def test_a_parents_spending_lands_when_its_children_land(yearly, monthly):
    """Not averaged into the parent's rhythm: a child with its own cadence and
    start day lands when it actually lands."""
    from datetime import timedelta

    from planning.services.budget_math import budget_events
    from utils.dates import get_todays_date_timezone_adjusted

    today = get_todays_date_timezone_adjusted()
    christmas = a_budget("Christmas", 0, yearly)
    monthly_child = a_budget("Christmas - Cards", 20, monthly, parent=christmas)
    monthly_child.start_day = today
    monthly_child.next_start = today
    monthly_child.save()

    events = budget_events(christmas, today, today + timedelta(days=120))

    assert len(events) >= 3
    assert all(amount == Decimal("-20") for _, amount in events)
