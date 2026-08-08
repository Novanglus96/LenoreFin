import pytest
from datetime import date
from decimal import Decimal
from accounts.models import Account, AccountType, Bank
from accounts.services.investment_performance import calculate_investment_return
from transactions.models import Transaction, TransactionType, TransactionStatus


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
    return Bank.objects.create(bank_name="Test Bank")


@pytest.fixture
def investment_account(db, bank, investment_account_type):
    return Account.objects.create(
        account_name="Test Investment",
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
        account_name="Test Checking",
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


@pytest.fixture
def transfer_type(db):
    return TransactionType.objects.create(transaction_type="Transfer")


@pytest.mark.django_db
@pytest.mark.service
def test_returns_none_for_non_investment_account(checking_account):
    result = calculate_investment_return(checking_account.id)
    assert result is None


@pytest.mark.django_db
@pytest.mark.service
def test_returns_none_for_nonexistent_account():
    result = calculate_investment_return(99999)
    assert result is None


@pytest.mark.django_db
@pytest.mark.service
def test_returns_none_with_no_cleared_transactions(investment_account):
    result = calculate_investment_return(investment_account.id)
    assert result is None


@pytest.mark.django_db
@pytest.mark.service
def test_returns_rate_with_income_transactions(
    investment_account, cleared_status, income_type
):
    six_months_ago = date.today().replace(year=date.today().year - 1) if date.today().month <= 6 else date(date.today().year, date.today().month - 6, 1)

    Transaction.objects.create(
        transaction_date=six_months_ago,
        total_amount=Decimal("500.00"),
        destination_account=investment_account,
        status=cleared_status,
        transaction_type=income_type,
        description="Dividend",
    )

    result = calculate_investment_return(investment_account.id)
    assert result is not None
    assert isinstance(result["rate"], float)
    assert result["period_months"] == 12
    assert result["data_points"] >= 1


@pytest.mark.django_db
@pytest.mark.service
def test_positive_return_when_account_grows(
    investment_account, cleared_status, income_type
):
    from dateutil.relativedelta import relativedelta

    six_months_ago = date.today() - relativedelta(months=6)

    Transaction.objects.create(
        transaction_date=six_months_ago,
        total_amount=Decimal("800.00"),
        destination_account=investment_account,
        status=cleared_status,
        transaction_type=income_type,
        description="Capital gain",
    )

    result = calculate_investment_return(investment_account.id)
    assert result is not None
    assert result["rate"] > 0


@pytest.mark.django_db
@pytest.mark.service
def test_transfer_excluded_from_intrinsic_return(
    investment_account, checking_account, cleared_status, transfer_type, income_type
):
    from dateutil.relativedelta import relativedelta

    six_months_ago = date.today() - relativedelta(months=6)

    # Large transfer IN — should not inflate the rate
    Transaction.objects.create(
        transaction_date=six_months_ago,
        total_amount=Decimal("50000.00"),
        destination_account=investment_account,
        source_account=checking_account,
        status=cleared_status,
        transaction_type=transfer_type,
        description="Contribution",
    )
    # Small organic gain
    Transaction.objects.create(
        transaction_date=six_months_ago,
        total_amount=Decimal("300.00"),
        destination_account=investment_account,
        status=cleared_status,
        transaction_type=income_type,
        description="Dividend",
    )

    result = calculate_investment_return(investment_account.id)
    assert result is not None
    # Rate should reflect the small gain, not be inflated to hundreds of percent
    assert abs(result["rate"]) < 50


@pytest.mark.django_db
@pytest.mark.service
def test_result_structure(investment_account, cleared_status, income_type):
    from dateutil.relativedelta import relativedelta

    Transaction.objects.create(
        transaction_date=date.today() - relativedelta(months=3),
        total_amount=Decimal("200.00"),
        destination_account=investment_account,
        status=cleared_status,
        transaction_type=income_type,
        description="Interest",
    )

    result = calculate_investment_return(investment_account.id)
    assert result is not None
    assert "rate" in result
    assert "period_months" in result
    assert "data_points" in result
    assert result["period_months"] == 12
    assert result["data_points"] >= 1
