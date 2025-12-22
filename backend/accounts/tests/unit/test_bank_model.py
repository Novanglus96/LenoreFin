import pytest
from accounts.models import Bank, Account


@pytest.mark.django_db
@pytest.mark.unit
def test_bank_creation():
    bank = Bank.objects.create(bank_name="Test Bank")

    assert bank.id is not None
    assert bank.bank_name == "Test Bank"


@pytest.mark.django_db
@pytest.mark.unit
def test_bank_str():
    bank = Bank.objects.create(bank_name="Test Bank")

    expected = "Test Bank"
    assert str(bank) == expected


@pytest.mark.django_db
@pytest.mark.unit
def test_bank_foreign_key_cascade_delete(test_checking_account, bank):

    assert Bank.objects.count() == 1

    bank.delete()

    assert Account.objects.count() == 0
