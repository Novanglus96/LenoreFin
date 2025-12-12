import pytest
from accounts.models import Bank, Account, AccountType


@pytest.fixture
def bank():
    return Bank.objects.create(bank_name="Test Bank")


@pytest.fixture
def checking_account_type():
    return AccountType.objects.create(
        account_type="Checking", color="#059669", icon="mdi-checkbook"
    )


@pytest.fixture
def test_checking_account(bank, checking_account_type):
    return Account.objects.create(
        account_name="Test Checking Account",
        account_type=checking_account_type,
        bank=bank,
    )
