import pytest
from administration.models import Payee
from django.db import IntegrityError


@pytest.mark.django_db
def test_payee_creation():
    payee = Payee.objects.create(payee_name="Payee")

    assert payee.payee_name == "Payee"


@pytest.mark.django_db
def test_payee_name_must_be_unique():
    Payee.objects.create(payee_name="Payee")

    with pytest.raises(IntegrityError):
        Payee.objects.create(payee_name="Payee")


@pytest.mark.django_db
def test_payee_string_representation():
    """Ensure __str__ returns the expected formatted string."""
    payee = Payee.objects.create(payee_name="Payee")

    expected = "Payee"
    assert str(payee) == expected
