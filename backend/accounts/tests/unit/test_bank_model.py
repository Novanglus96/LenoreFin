import pytest
from accounts.models import Bank, Account
from accounts.dto import DomainBank
from accounts.mappers import domain_bank_to_schema


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


@pytest.mark.django_db
@pytest.mark.unit
def test_bank_logo_url_stored():
    bank = Bank.objects.create(
        bank_name="Ally Financial",
        logo_url="https://icon.horse/icon/ally.com",
    )

    bank.refresh_from_db()
    assert bank.logo_url == "https://icon.horse/icon/ally.com"


@pytest.mark.django_db
@pytest.mark.unit
def test_bank_logo_url_nullable():
    bank = Bank.objects.create(bank_name="No Logo Bank")

    assert bank.logo_url is None


@pytest.mark.unit
def test_domain_bank_to_schema_includes_logo_url():
    domain = DomainBank(id=1, bank_name="Ally Financial", logo_url="https://icon.horse/icon/ally.com")
    schema = domain_bank_to_schema(domain)

    assert schema.logo_url == "https://icon.horse/icon/ally.com"


@pytest.mark.unit
def test_domain_bank_to_schema_logo_url_none():
    domain = DomainBank(id=1, bank_name="No Logo Bank", logo_url=None)
    schema = domain_bank_to_schema(domain)

    assert schema.logo_url is None
