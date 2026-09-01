"""Everything that funds a bucket, not only the reminder it points at.

`Bucket.reminder` names the transfer the plan *adjusts*. It is not the only
money arriving. Ally - Kids is the case that forced this: the linked
`Transfer to Kids` moves 85.00 a fortnight while an undeclared
`DCA Transfer to Ally` moves 277.77 — three times as much — and the page
reported that the bucket received 85.

The sources are derived from the reminders rather than declared on the bucket,
so there is no way to forget to write one down. That is the whole point: a
declared list is only as good as the last person to maintain it.
"""

from decimal import Decimal

import pytest

from planning.services.savings_plan import funding_sources

PER_YEAR = Decimal("26.0893")


@pytest.fixture
def biweekly():
    """A real fortnight.

    The shared `test_repeat` fixture is days=1, weeks=1, months=1, years=1 —
    about 403 days, which is not a cadence anyone has. These tests are about
    converting between cadences, so they need one that means something.
    """
    from reminders.models import Repeat

    return Repeat.objects.create(repeat_name="Every 2 Weeks", weeks=2)


@pytest.fixture
def bucket(test_savings_account, test_reminder):
    from planning.models import Bucket

    # The fixture reminder pays checking -> savings, which is the shape of a
    # bucket's own funding transfer.
    return Bucket.objects.create(
        name="Kids",
        contribution_per_paycheck=Decimal("85.00"),
        account=test_savings_account,
        reminder=test_reminder,
        active=True,
    )


def a_reminder(destination, amount, description, repeat, source, tag, ttype):
    from reminders.models import Reminder

    return Reminder.objects.create(
        tag=tag,
        amount=amount,
        reminder_source_account=source,
        reminder_destination_account=destination,
        description=description,
        transaction_type=ttype,
        repeat=repeat,
    )


@pytest.mark.service
@pytest.mark.django_db
def test_the_linked_reminder_is_the_adjustable_one(bucket, test_reminder):
    sources = funding_sources(bucket, PER_YEAR)

    assert [s.reminder_id for s in sources] == [test_reminder.id]
    assert sources[0].adjustable is True


@pytest.mark.service
@pytest.mark.django_db
def test_an_undeclared_reminder_paying_in_is_still_funding(
    bucket, test_savings_account, test_checking_account, biweekly,
    test_tag, test_expense_transaction_type,
):
    """The bug this exists for.

    Nothing links this reminder to the bucket. It pays into the account, so it
    funds it, and the plan has to be able to say so.
    """
    a_reminder(
        test_savings_account, Decimal("-277.77"), "DCA Transfer to Ally",
        biweekly, test_checking_account, test_tag,
        test_expense_transaction_type,
    )

    sources = funding_sources(bucket, PER_YEAR)
    other = [s for s in sources if not s.adjustable]

    assert len(other) == 1
    assert other[0].description == "DCA Transfer to Ally"
    assert other[0].per_paycheck == Decimal("277.77")


@pytest.mark.service
@pytest.mark.django_db
def test_money_leaving_the_account_is_not_funding(
    bucket, test_savings_account, test_checking_account, test_repeat,
    test_tag, test_expense_transaction_type,
):
    """A reimbursement out of the bucket is an obligation, not a source.

    Ally - Kids sends money back to checking every fortnight. Counting that as
    funding would report the bucket as better off for spending its own money.
    """
    a_reminder(
        test_checking_account, Decimal("-18.00"), "Transfer to Checking (Kids)",
        test_repeat, test_savings_account, test_tag,
        test_expense_transaction_type,
    )

    sources = funding_sources(bucket, PER_YEAR)

    assert "Transfer to Checking (Kids)" not in [s.description for s in sources]


@pytest.mark.service
@pytest.mark.django_db
def test_a_different_cadence_is_converted_not_added_raw(
    bucket, test_savings_account, test_checking_account, test_tag,
    test_expense_transaction_type,
):
    """A monthly 100 is not 100 a paycheck.

    Everything the planner reports is per paycheck, so a source on its own
    cadence has to be converted before it can be compared with one.
    """
    from reminders.models import Repeat

    monthly = Repeat.objects.create(repeat_name="Monthly", months=1)
    a_reminder(
        test_savings_account, Decimal("-100.00"), "Monthly top-up",
        monthly, test_checking_account, test_tag,
        test_expense_transaction_type,
    )

    source = next(
        s for s in funding_sources(bucket, PER_YEAR)
        if s.description == "Monthly top-up"
    )

    # 100 a month over 26.0893 paychecks a year is 46.00, not 100.
    assert source.per_paycheck == Decimal("46.00")


@pytest.mark.service
@pytest.mark.django_db
def test_a_one_off_is_not_reported_as_a_rate(
    bucket, test_savings_account, test_checking_account, test_tag,
    test_expense_transaction_type,
):
    """It is a dated event on the path. Calling it a rate implies it recurs."""
    a_reminder(
        test_savings_account, Decimal("-500.00"), "One-off top-up",
        None, test_checking_account, test_tag, test_expense_transaction_type,
    )

    assert "One-off top-up" not in [
        s.description for s in funding_sources(bucket, PER_YEAR)
    ]


@pytest.mark.unit
@pytest.mark.django_db
def test_the_adjustable_reminder_must_pay_into_the_bucket(
    test_savings_account, test_checking_account, test_repeat, test_tag,
    test_expense_transaction_type,
):
    """Otherwise the plan raises a figure that never reaches this bucket."""
    from django.core.exceptions import ValidationError

    from planning.models import Bucket

    elsewhere = a_reminder(
        test_checking_account, Decimal("-50.00"), "Pays somewhere else",
        test_repeat, test_savings_account, test_tag,
        test_expense_transaction_type,
    )
    bucket = Bucket(
        name="Wrong link",
        contribution_per_paycheck=Decimal("50.00"),
        account=test_savings_account,
        reminder=elsewhere,
    )

    with pytest.raises(ValidationError, match="does not pay into"):
        bucket.full_clean()


@pytest.mark.service
@pytest.mark.django_db
def test_a_main_tag_claims_children_that_do_not_exist_yet(
    test_savings_account, test_reminder,
):
    """The difference between a rule and a snapshot.

    Naming child tags one by one is a photograph of the tag list on the day
    someone set the bucket up. Add a subcategory later and the bucket that
    obviously owns it does not claim it, the spending lands in a category no
    bucket owns, and nothing anywhere says so — which is exactly how a gift
    shortfall hid for years.
    """
    from planning.models import Bucket
    from tags.models import MainTag, SubTag, Tag

    kids = MainTag.objects.create(tag_name="Kids", slug="kids", tag_type_id=1)
    clothes = SubTag.objects.create(tag_name="Clothes", tag_type_id=1)
    Tag.objects.create(
        parent=kids, child=clothes, tag_type_id=1, slug="kids-clothes"
    )

    bucket = Bucket.objects.create(
        name="Kids bucket",
        contribution_per_paycheck=Decimal("85.00"),
        account=test_savings_account,
        reminder=test_reminder,
    )
    bucket.scope_main_tags.set([kids])
    assert bucket.claimed_tags().count() == 1

    # A category nobody had thought of when the bucket was set up.
    sports = SubTag.objects.create(tag_name="Sports", tag_type_id=1)
    Tag.objects.create(
        parent=kids, child=sports, tag_type_id=1, slug="kids-sports"
    )

    assert bucket.claimed_tags().count() == 2


@pytest.mark.service
@pytest.mark.django_db
def test_naming_a_tag_and_its_family_does_not_claim_it_twice(
    test_savings_account, test_reminder,
):
    """Both ways of claiming are allowed; the union is what counts."""
    from planning.models import Bucket
    from tags.models import MainTag, SubTag, Tag

    kids = MainTag.objects.create(tag_name="Kids", slug="kids", tag_type_id=1)
    clothes = SubTag.objects.create(tag_name="Clothes", tag_type_id=1)
    tag = Tag.objects.create(
        parent=kids, child=clothes, tag_type_id=1, slug="kids-clothes"
    )

    bucket = Bucket.objects.create(
        name="Kids bucket",
        contribution_per_paycheck=Decimal("85.00"),
        account=test_savings_account,
        reminder=test_reminder,
    )
    bucket.scope_tags.set([tag])
    bucket.scope_main_tags.set([kids])

    assert bucket.claimed_tags().count() == 1
