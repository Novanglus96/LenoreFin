import pytest
from planning.models import Bucket
from django.core.exceptions import ValidationError
from django.db import IntegrityError


@pytest.mark.django_db
def test_bucket_creation():
    bucket = Bucket.objects.create(
        name="Bucket",
        contribution_per_paycheck=1.00,
        minimum_per_paycheck=1.00,
        mode="maintain",
        minimum_balance=1.00,
        active=True,
    )

    assert bucket.id is not None
    assert bucket.name == "Bucket"
    assert bucket.contribution_per_paycheck == 1.00
    assert bucket.minimum_per_paycheck == 1.00
    assert bucket.mode == "maintain"
    assert bucket.minimum_balance == 1.00
    assert bucket.active


@pytest.mark.django_db
def test_bucket_defaults():
    bucket = Bucket.objects.create(
        name="Bucket",
    )

    assert bucket.id is not None
    assert bucket.contribution_per_paycheck == 0.00
    # Null, not zero: "work it out from the budgets and obligations" is a
    # different statement from "nothing is required here".
    assert bucket.minimum_per_paycheck is None
    # Cover is the honest default: a bucket nobody has told anything about
    # funds what it must spend and asks for nothing on top.
    assert bucket.mode == "cover"
    assert bucket.minimum_balance is None
    assert bucket.goal_amount is None
    assert bucket.sweep is False
    assert bucket.priority == 100
    assert bucket.active


@pytest.mark.django_db
def test_conitrbution_uniqueness():
    Bucket.objects.create(
        name="Bucket",
    )

    with pytest.raises(IntegrityError):
        Bucket.objects.create(
            name="Bucket",
        )


@pytest.mark.django_db
def test_bucket_string_representation():
    bucket = Bucket.objects.create(
        name="Bucket",
    )
    expected = "Bucket"

    assert str(bucket) == expected


# ---------------------------------------------------------------------------
# A field the chosen mode would ignore is rejected rather than stored.
#
# The old scheme inferred intent from which nullable fields were set, so every
# combination was legal and some of them meant nothing. Storing a goal amount
# on a Cover bucket is a statement the plan will never honour, and the person
# who typed it has no way to find that out.
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_maintain_needs_the_balance_it_is_maintaining(test_savings_account):
    bucket = Bucket(
        name="Vacation", mode="maintain", account=test_savings_account
    )
    with pytest.raises(ValidationError, match="needs the balance to hold"):
        bucket.full_clean()


@pytest.mark.django_db
def test_a_goal_needs_both_an_amount_and_a_date(test_savings_account):
    """An amount with no date is a Maintain wearing a goal's clothes.

    That confusion is the entire reason modes exist, so it cannot be allowed
    back in through a half-filled Goal.
    """
    bucket = Bucket(
        name="Vacation",
        mode="goal",
        goal_amount=4000,
        account=test_savings_account,
    )
    with pytest.raises(ValidationError, match="both an amount and the date"):
        bucket.full_clean()


@pytest.mark.django_db
def test_a_cover_bucket_may_not_carry_a_balance_target(test_savings_account):
    bucket = Bucket(
        name="Grocery",
        mode="cover",
        minimum_balance=500,
        account=test_savings_account,
    )
    with pytest.raises(ValidationError, match="only applies to a bucket set to Maintain"):
        bucket.full_clean()


@pytest.mark.django_db
def test_a_sweep_may_not_also_ask_for_a_balance(test_savings_account):
    """A sweep takes what is left, so a target on it is a contradiction.

    Previously a rule of its own; now it falls out of the mode being a single
    choice — Maximise simply is not the mode that carries a balance.
    """
    bucket = Bucket(
        name="Leftovers",
        mode="maximise",
        minimum_balance=500,
        account=test_savings_account,
    )
    with pytest.raises(ValidationError, match="only applies to a bucket set to Maintain"):
        bucket.full_clean()


@pytest.mark.django_db
def test_a_balance_target_needs_an_account_to_be_about():
    bucket = Bucket(name="Vacation", mode="maintain", minimum_balance=4000)
    with pytest.raises(ValidationError, match="Set an account"):
        bucket.full_clean()
