"""Funding a bucket from what its tags actually cost.

Budgets are the better input wherever one exists — they are the user's own
statement of intent. But some spending is real, recurring, and never going to
be written down: a dozen birthdays spread unevenly across the year, where
maintaining a budget per person is a chore nobody keeps up. For those, twelve
months of measured spending is the only evidence there is.

The trap these tests exist to hold shut is double counting. A bucket can carry
a budget *and* the tags that budget already covers — this household's Gifts
bucket carries the Christmas budget and 26 gift tags, 22 of which the budget
lists. Counting both would fund Christmas twice.
"""

from datetime import timedelta
from decimal import Decimal

import pytest

pytestmark = [pytest.mark.service, pytest.mark.django_db]


@pytest.fixture
def gift_tags(db):
    from tags.models import MainTag, SubTag, Tag, TagType

    tag_type, _ = TagType.objects.get_or_create(tag_type="Expense")
    gifts = MainTag.objects.create(tag_name="Gifts", tag_type=tag_type)
    christmas = MainTag.objects.create(tag_name="Christmas", tag_type=tag_type)
    ellie = SubTag.objects.create(tag_name="Ellie", tag_type=tag_type)
    return {
        "gifts": Tag.objects.create(parent=gifts, tag_type=tag_type),
        "christmas": Tag.objects.create(parent=christmas, tag_type=tag_type),
        "christmas_ellie": Tag.objects.create(
            parent=christmas, child=ellie, tag_type=tag_type
        ),
    }


def a_spend(tag, amount, days_ago, status):
    """One expense, `days_ago` back, tagged."""
    from transactions.models import Transaction, TransactionDetail
    from utils.dates import get_todays_date_timezone_adjusted

    when = get_todays_date_timezone_adjusted() - timedelta(days=days_ago)
    transaction = Transaction.objects.create(
        transaction_date=when,
        total_amount=Decimal(str(amount)),
        description="gift",
        status=status,
    )
    TransactionDetail.objects.create(
        transaction=transaction, detail_amt=Decimal(str(amount)), tag=tag
    )
    return transaction


@pytest.fixture
def cleared_status(db):
    from transactions.models import TransactionStatus

    status, _ = TransactionStatus.objects.get_or_create(
        transaction_status="Cleared", defaults={"slug": "cleared"}
    )
    return status


def a_contribution(name="Gifts"):
    from planning.models import Contribution

    return Contribution.objects.create(
        contribution=name, per_paycheck=Decimal("45.00"), active=True
    )


def horizon():
    from planning.services.planner import DAYS_PER_YEAR
    from utils.dates import get_todays_date_timezone_adjusted

    today = get_todays_date_timezone_adjusted()
    return today, today + timedelta(days=int(DAYS_PER_YEAR))


def test_spending_on_a_linked_tag_is_measured(gift_tags, cleared_status):
    from planning.services.savings_plan import tag_spend_events

    contribution = a_contribution()
    contribution.tags.set([gift_tags["gifts"]])
    a_spend(gift_tags["gifts"], -60, 100, cleared_status)
    a_spend(gift_tags["gifts"], -40, 30, cleared_status)

    today, end = horizon()
    events, total, names = tag_spend_events(contribution, today, end)

    assert total == Decimal("100.00")
    assert names == ["Gifts"]
    # Replayed a year on: a birthday in March recurs in March, so the dates
    # carry over rather than being flattened into a rate.
    assert [when for when, _ in events] == [
        today + timedelta(days=265),
        today + timedelta(days=335),
    ]


def test_a_tag_its_budget_already_covers_is_not_counted_twice(
    gift_tags, cleared_status
):
    """The whole reason this function takes the budgets into account."""
    import json

    from planning.models import Budget
    from planning.services.savings_plan import tag_spend_events

    contribution = a_contribution()
    budget = Budget.objects.create(
        name="Christmas",
        amount=Decimal("1995.00"),
        tag_ids=json.dumps([gift_tags["christmas"].pk]),
    )
    contribution.budgets.set([budget])
    contribution.tags.set([gift_tags["christmas"], gift_tags["gifts"]])
    a_spend(gift_tags["christmas"], -500, 60, cleared_status)
    a_spend(gift_tags["gifts"], -75, 60, cleared_status)

    today, end = horizon()
    _, total, names = tag_spend_events(contribution, today, end)

    # Only the birthday spending. The 500 of Christmas is already in the
    # budget, and the budget is what funds it.
    assert total == Decimal("75.00")
    assert names == ["Gifts"]


def test_a_refund_nets_off_rather_than_counting_as_more_to_find(
    gift_tags, cleared_status
):
    from planning.services.savings_plan import tag_spend_events

    contribution = a_contribution()
    contribution.tags.set([gift_tags["gifts"]])
    a_spend(gift_tags["gifts"], -80, 50, cleared_status)
    a_spend(gift_tags["gifts"], 30, 40, cleared_status)

    _, total, _ = tag_spend_events(contribution, *horizon())

    assert total == Decimal("50.00")


def test_a_bucket_with_no_tags_measures_nothing(gift_tags, cleared_status):
    """Measurement is opt-in. A bucket saving toward a stated target is not
    doing so because of what it happened to spend last year."""
    from planning.services.savings_plan import tag_spend_events

    contribution = a_contribution()
    a_spend(gift_tags["gifts"], -500, 60, cleared_status)

    events, total, names = tag_spend_events(contribution, *horizon())

    assert (events, total, names) == ([], Decimal("0.00"), [])


def test_spending_older_than_a_year_is_out_of_the_window(
    gift_tags, cleared_status
):
    from planning.services.savings_plan import tag_spend_events

    contribution = a_contribution()
    contribution.tags.set([gift_tags["gifts"]])
    a_spend(gift_tags["gifts"], -200, 400, cleared_status)

    _, total, _ = tag_spend_events(contribution, *horizon())

    assert total == Decimal("0.00")
