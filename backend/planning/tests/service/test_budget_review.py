"""Budgets checked against what actually happened.

Budgets are the only thing the savings plan acts on, which makes them worth
revisiting: a decision nobody returns to drifts, and a category nobody wrote
down at all is invisible. This is the loop that closes — measurement proposes,
the budget decides, the plan follows.
"""

import json
from datetime import timedelta
from decimal import Decimal

import pytest

from planning.services.budget_review import review_budgets

pytestmark = [pytest.mark.service, pytest.mark.django_db]


@pytest.fixture
def yearly(db):
    from reminders.models import Repeat

    repeat, _ = Repeat.objects.get_or_create(
        repeat_name="Every Year", defaults={"years": 1, "slug": "every-year"}
    )
    return repeat


@pytest.fixture
def spend_tag(db):
    from tags.models import MainTag, Tag, TagType

    tag_type, _ = TagType.objects.get_or_create(tag_type="Expense")
    main = MainTag.objects.create(tag_name="Christmas", tag_type=tag_type)
    return Tag.objects.create(parent=main, tag_type=tag_type)


@pytest.fixture
def cleared(db):
    from transactions.models import TransactionStatus

    status, _ = TransactionStatus.objects.get_or_create(
        transaction_status="Cleared", defaults={"slug": "cleared"}
    )
    return status


def spent(tag, amount, status, days_ago=60):
    from transactions.models import Transaction, TransactionDetail
    from utils.dates import get_todays_date_timezone_adjusted

    txn = Transaction.objects.create(
        transaction_date=get_todays_date_timezone_adjusted()
        - timedelta(days=days_ago),
        total_amount=Decimal(str(amount)),
        description="spend",
        status=status,
    )
    TransactionDetail.objects.create(
        transaction=txn, detail_amt=Decimal(str(amount)), tag=tag
    )


def a_budget(name, amount, tag, repeat):
    from planning.models import Budget

    return Budget.objects.create(
        name=name,
        amount=Decimal(str(amount)),
        repeat=repeat,
        tag_ids=json.dumps([tag.pk]),
        active=True,
    )


def today():
    from utils.dates import get_todays_date_timezone_adjusted

    return get_todays_date_timezone_adjusted()


def test_a_budget_that_matches_reality_is_left_alone(spend_tag, cleared, yearly):
    a_budget("Christmas", 500, spend_tag, yearly)
    spent(spend_tag, -480, cleared)

    review = review_budgets(today())

    assert review.suggestions == []


def test_a_budget_well_under_what_was_spent_is_raised(
    spend_tag, cleared, yearly
):
    a_budget("Christmas", 500, spend_tag, yearly)
    spent(spend_tag, -900, cleared)

    review = review_budgets(today())

    assert [s.kind for s in review.suggestions] == ["raise"]
    assert review.suggestions[0].suggested_amount == Decimal("900.00")
    assert review.suggestions[0].measured_per_year == Decimal("900.00")


def test_a_small_difference_is_not_worth_saying(spend_tag, cleared, yearly):
    """Both bars have to be cleared. Ten per cent of a 60 budget is six
    pounds, and nobody wants to be told about six pounds."""
    a_budget("Christmas", 500, spend_tag, yearly)
    spent(spend_tag, -530, cleared)

    assert review_budgets(today()).suggestions == []


def test_spending_a_bucket_owns_with_no_budget_becomes_a_new_one(
    spend_tag, cleared
):
    from planning.models import Bucket

    bucket = Bucket.objects.create(
        name="Gifts", contribution_per_paycheck=Decimal("45.00"), active=True
    )
    bucket.scope_tags.set([spend_tag])
    spent(spend_tag, -2023.34, cleared)

    review = review_budgets(today())

    assert [s.kind for s in review.suggestions] == ["create"]
    suggestion = review.suggestions[0]
    assert suggestion.bucket_name == "Gifts"
    assert suggestion.measured_per_year == Decimal("2023.34")
    # Named per paycheck too, because that is the unit the plan is stated in.
    assert suggestion.per_paycheck_effect == Decimal("77.55")


def test_unbudgeted_spending_nobody_claimed_is_not_reported(
    spend_tag, cleared
):
    """Unscoped, this report is meaningless.

    Transfers, income and card payments dwarf every real category — a review
    led by "Transfer: 230,990 unbudgeted" is one nobody reads twice. Only
    spending some bucket has claimed through its tags counts.
    """
    spent(spend_tag, -5000, cleared)

    assert review_budgets(today()).suggestions == []


def test_two_budgets_covering_one_tag_cannot_be_checked(
    spend_tag, cleared, yearly
):
    """The Christmas trap: a parent budget and twenty per-person budgets over
    the same tags. Both look overspent against the same money, so "raise
    John's gift budget from 100 to 524" would be founded on money the parent
    budget already accounts for."""
    a_budget("Christmas", 1995, spend_tag, yearly)
    a_budget("Christmas - John", 100, spend_tag, yearly)
    spent(spend_tag, -900, cleared)

    review = review_budgets(today())

    assert [s.kind for s in review.suggestions] == ["overlap"]
    assert "not both" in review.suggestions[0].why
    assert review.notes


@pytest.mark.service
@pytest.mark.django_db
def test_spending_a_reminder_already_covers_is_not_called_unbudgeted(
    cleared, test_checking_account, test_savings_account, test_tag,
    test_expense_transaction_type,
):
    """Scheduled is a stronger statement than budgeted, not a weaker one.

    Kids/Child Care is the case: 10,744.11 went out on it last year with no
    budget, but 8,592.00 of that is a monthly preschool reminder already on the
    path. Suggesting a budget for the measured figure would fund the preschool
    twice and ask for 330 a paycheck that is already committed.
    """
    from reminders.models import Reminder, Repeat
    from planning.models import Bucket
    from utils.dates import get_todays_date_timezone_adjusted

    today = get_todays_date_timezone_adjusted()
    monthly = Repeat.objects.create(repeat_name="Monthly", months=1)

    bucket = Bucket.objects.create(
        name="Kids",
        contribution_per_paycheck=Decimal("85.00"),
        account=test_savings_account,
        active=True,
    )
    bucket.scope_tags.set([test_tag])

    # 1,200 a year of it is scheduled.
    Reminder.objects.create(
        tag=test_tag,
        amount=Decimal("-100.00"),
        reminder_source_account=test_checking_account,
        reminder_destination_account=test_savings_account,
        description="Preschool",
        transaction_type=test_expense_transaction_type,
        repeat=monthly,
    )
    # 1,500 was actually spent on the tag.
    spent(test_tag, "-1500.00", cleared, days_ago=30)

    review = review_budgets(today)
    created = [s for s in review.suggestions if s.kind == "create"]

    assert len(created) == 1
    # 1,500 spent less 1,200 already committed, not the full 1,500.
    assert created[0].measured_per_year == Decimal("300.00")
    assert "already committed by reminders" in created[0].why


@pytest.mark.service
@pytest.mark.django_db
def test_accepting_a_suggestion_settles_it(
    cleared, test_checking_account, test_savings_account, test_tag,
    test_expense_transaction_type,
):
    """A review whose advice undoes itself is worse than none.

    `create` proposes a budget for the spending no reminder covers. If `raise`
    then compares that budget against the *un-netted* measurement, accepting
    the first suggestion immediately produces a second one telling you to fund
    the scheduled part all over again — on real data, 329.33 a paycheck to pay
    the preschool twice. The two halves have to net the same way.
    """
    from decimal import Decimal

    from reminders.models import Reminder, Repeat
    from planning.models import Bucket, Budget
    from utils.dates import get_todays_date_timezone_adjusted

    today = get_todays_date_timezone_adjusted()
    monthly = Repeat.objects.create(repeat_name="Monthly", months=1)

    bucket = Bucket.objects.create(
        name="Kids",
        contribution_per_paycheck=Decimal("85.00"),
        account=test_savings_account,
        active=True,
    )
    bucket.scope_tags.set([test_tag])
    Reminder.objects.create(
        tag=test_tag, amount=Decimal("-100.00"),
        reminder_source_account=test_checking_account,
        reminder_destination_account=test_savings_account,
        description="Preschool",
        transaction_type=test_expense_transaction_type, repeat=monthly,
    )
    spent(test_tag, "-1500.00", cleared, days_ago=30)

    proposed = next(
        s for s in review_budgets(today).suggestions if s.kind == "create"
    )
    assert proposed.suggested_per_year == Decimal("300.00")

    # Accept it, exactly as written.
    budget = Budget.objects.create(
        name=proposed.budget_name,
        tag_ids=json.dumps([test_tag.id]),
        amount=proposed.suggested_per_year,
        repeat=Repeat.objects.create(repeat_name="Yearly", years=1),
        active=True,
    )
    bucket.budgets.set([budget])

    after = review_budgets(today).suggestions

    assert [s for s in after if s.budget_name == proposed.budget_name] == [], (
        "accepting the suggestion produced another suggestion about it"
    )
