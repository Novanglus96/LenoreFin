import pytest
from planning.models import Contribution
from django.db import IntegrityError


@pytest.mark.django_db
def test_contribution_creation():
    contribution = Contribution.objects.create(
        contribution="Contribution",
        per_paycheck=1.00,
        minimum_per_paycheck=1.00,
        target_balance=1.00,
        active=True,
    )

    assert contribution.id is not None
    assert contribution.contribution == "Contribution"
    assert contribution.per_paycheck == 1.00
    assert contribution.minimum_per_paycheck == 1.00
    assert contribution.target_balance == 1.00
    assert contribution.active


@pytest.mark.django_db
def test_contribution_defaults():
    contribution = Contribution.objects.create(
        contribution="Contribution",
    )

    assert contribution.id is not None
    assert contribution.per_paycheck == 0.00
    # Null, not zero: "work it out from the budgets and obligations" is a
    # different statement from "nothing is required here".
    assert contribution.minimum_per_paycheck is None
    assert contribution.target_balance is None
    assert contribution.sweep is False
    assert contribution.priority == 100
    assert contribution.active


@pytest.mark.django_db
def test_conitrbution_uniqueness():
    Contribution.objects.create(
        contribution="Contribution",
    )

    with pytest.raises(IntegrityError):
        Contribution.objects.create(
            contribution="Contribution",
        )


@pytest.mark.django_db
def test_contribution_string_representation():
    contribution = Contribution.objects.create(
        contribution="Contribution",
    )
    expected = "Contribution"

    assert str(contribution) == expected
