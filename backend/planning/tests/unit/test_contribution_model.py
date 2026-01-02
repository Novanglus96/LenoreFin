import pytest
from planning.models import Contribution
from django.db import IntegrityError


@pytest.mark.django_db
def test_contribution_creation():
    contribution = Contribution.objects.create(
        contribution="Contribution",
        per_paycheck=1.00,
        emergency_amt=1.00,
        emergency_diff=0.00,
        cap=1.00,
        active=True,
    )

    assert contribution.id is not None
    assert contribution.contribution == "Contribution"
    assert contribution.per_paycheck == 1.00
    assert contribution.emergency_amt == 1.00
    assert contribution.emergency_diff == 0.00
    assert contribution.cap == 1.00
    assert contribution.active


@pytest.mark.django_db
def test_contribution_defaults():
    contribution = Contribution.objects.create(
        contribution="Contribution",
    )

    assert contribution.id is not None
    assert contribution.per_paycheck == 0.00
    assert contribution.emergency_amt == 0.00
    assert contribution.emergency_diff == 0.00
    assert contribution.cap == 0.00
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
