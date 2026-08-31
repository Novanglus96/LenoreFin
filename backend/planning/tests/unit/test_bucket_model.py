import pytest
from planning.models import Bucket
from django.db import IntegrityError


@pytest.mark.django_db
def test_bucket_creation():
    bucket = Bucket.objects.create(
        name="Bucket",
        contribution_per_paycheck=1.00,
        minimum_per_paycheck=1.00,
        target_balance=1.00,
        active=True,
    )

    assert bucket.id is not None
    assert bucket.name == "Bucket"
    assert bucket.contribution_per_paycheck == 1.00
    assert bucket.minimum_per_paycheck == 1.00
    assert bucket.target_balance == 1.00
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
    assert bucket.target_balance is None
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
