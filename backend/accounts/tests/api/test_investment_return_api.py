import pytest
from datetime import date
from decimal import Decimal
from accounts.models import Account, AccountType, Bank
from transactions.models import Transaction, TransactionType, TransactionStatus


AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.fixture
def investment_account_type(db):
    return AccountType.objects.create(
        account_type="Investment", color="#059669", icon="mdi-chart-line", slug="investment"
    )


@pytest.fixture
def checking_account_type(db):
    return AccountType.objects.create(
        account_type="Checking", color="#0099cc", icon="mdi-checkbook", slug="checking"
    )


@pytest.fixture
def bank(db):
    return Bank.objects.create(bank_name="API Test Bank")


@pytest.fixture
def investment_account(db, bank, investment_account_type):
    return Account.objects.create(
        account_name="API Investment",
        account_type=investment_account_type,
        opening_balance=Decimal("10000.00"),
        archive_balance=Decimal("0.00"),
        annual_rate=Decimal("0.00"),
        active=True,
        open_date=date.today(),
        bank=bank,
        calculate_interest=False,
        calculate_payments=False,
        payment_strategy="F",
    )


@pytest.fixture
def checking_account(db, bank, checking_account_type):
    return Account.objects.create(
        account_name="API Checking",
        account_type=checking_account_type,
        opening_balance=Decimal("5000.00"),
        archive_balance=Decimal("0.00"),
        annual_rate=Decimal("0.00"),
        active=True,
        open_date=date.today(),
        bank=bank,
        calculate_interest=False,
        calculate_payments=False,
        payment_strategy="F",
    )


@pytest.fixture
def cleared_status(db):
    return TransactionStatus.objects.create(transaction_status="Cleared")


@pytest.fixture
def income_type(db):
    return TransactionType.objects.create(transaction_type="Income")


@pytest.mark.django_db
@pytest.mark.api
def test_investment_return_insufficient_data(api_client, investment_account):
    response = api_client.get(
        f"/accounts/{investment_account.id}/investment-return",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sufficient_data"] is False
    assert data["rate"] is None
    assert data["period_months"] == 12
    assert data["data_points"] == 0


@pytest.mark.django_db
@pytest.mark.api
def test_investment_return_with_data(
    api_client, investment_account, cleared_status, income_type
):
    from dateutil.relativedelta import relativedelta

    Transaction.objects.create(
        transaction_date=date.today() - relativedelta(months=3),
        total_amount=Decimal("500.00"),
        destination_account=investment_account,
        status=cleared_status,
        transaction_type=income_type,
        description="Dividend",
    )

    response = api_client.get(
        f"/accounts/{investment_account.id}/investment-return",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sufficient_data"] is True
    assert data["rate"] is not None
    assert isinstance(data["rate"], float)
    assert data["data_points"] >= 1


@pytest.mark.django_db
@pytest.mark.api
def test_investment_return_non_investment_account(api_client, checking_account):
    response = api_client.get(
        f"/accounts/{checking_account.id}/investment-return",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sufficient_data"] is False
    assert data["rate"] is None


@pytest.mark.django_db
@pytest.mark.api
def test_investment_return_nonexistent_account(api_client):
    response = api_client.get(
        "/accounts/99999/investment-return",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sufficient_data"] is False
