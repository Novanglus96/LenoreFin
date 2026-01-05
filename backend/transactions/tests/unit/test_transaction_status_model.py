import pytest
from transactions.models import TransactionStatus
from django.db import IntegrityError


@pytest.mark.django_db
def test_transaction_status_creation():
    transaction_status = TransactionStatus.objects.create(
        transaction_status="Pending"
    )

    assert transaction_status.id is not None
    assert transaction_status.transaction_status == "Pending"


@pytest.mark.django_db
def test_transaction_status_string_representation():
    transaction_status = TransactionStatus.objects.create(
        transaction_status="Pending"
    )
    expected = "Pending"

    assert transaction_status.id is not None
    assert str(transaction_status) == expected


@pytest.mark.django_db
def test_transaction_status_uniqueness():
    TransactionStatus.objects.create(transaction_status="Pending")

    with pytest.raises(IntegrityError):
        TransactionStatus.objects.create(transaction_status="Pending")
