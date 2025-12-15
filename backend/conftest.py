import pytest
from accounts.models import Bank, Account, AccountType
from tags.models import TagType, MainTag, SubTag, Tag
from django.utils import timezone
import pytz
import os


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.fixture
def bank():
    return Bank.objects.create(bank_name="Test Bank")


@pytest.fixture
def tag_type_expense():
    return TagType.objects.create(tag_type="Expense")


@pytest.fixture
def test_main_tag(tag_type_expense):
    return MainTag.objects.create(
        tag_name="Main Test", tag_type=tag_type_expense
    )


@pytest.fixture
def test_sub_tag(tag_type_expense):
    return SubTag.objects.create(tag_name="Sub Test", tag_type=tag_type_expense)


@pytest.fixture
def test_tag(tag_type_expense, test_sub_tag, test_main_tag):
    return Tag.objects.create(
        parent=test_main_tag, child=test_sub_tag, tag_type=tag_type_expense
    )


@pytest.fixture
def checking_account_type():
    return AccountType.objects.create(
        account_type="Checking", color="#059669", icon="mdi-checkbook"
    )


@pytest.fixture
def savings_account_type():
    return AccountType.objects.create(
        account_type="Savings", color="#059669", icon="mdi-checkbook"
    )


@pytest.fixture
def credit_card_account_type():
    return AccountType.objects.create(
        account_type="Credit Card", color="#059669", icon="mdi-checkbook"
    )


@pytest.fixture
def test_checking_account(bank, checking_account_type):
    return Account.objects.create(
        account_name="Test Checking Account",
        account_type=checking_account_type,
        opening_balance=55.55,
        annual_rate=5.55,
        active=True,
        open_date=current_date(),
        statement_cycle_length=1,
        statement_cycle_period="m",
        credit_limit=55555,
        bank=bank,
        last_statement_amount=555.55,
        archive_balance=555.55,
        funding_account=None,
        calculate_payments=False,
        calculate_interest=False,
        payment_strategy="F",
        payment_amount=55.55,
        minimum_payment_amount=25.00,
        statement_day=15,
        due_day=15,
        pay_day=15,
    )


@pytest.fixture
def test_savings_account(bank, savings_account_type):
    return Account.objects.create(
        account_name="Test Savings Account",
        account_type=savings_account_type,
        opening_balance=55.55,
        annual_rate=5.55,
        active=True,
        open_date=current_date(),
        statement_cycle_length=1,
        statement_cycle_period="m",
        credit_limit=55555,
        bank=bank,
        last_statement_amount=555.55,
        archive_balance=555.55,
        funding_account=None,
        calculate_payments=False,
        calculate_interest=False,
        payment_strategy="F",
        payment_amount=55.55,
        minimum_payment_amount=25.00,
        statement_day=15,
        due_day=15,
        pay_day=15,
    )


@pytest.fixture
def test_credit_card_account(bank, credit_card_account_type):
    return Account.objects.create(
        account_name="Test Credit Card Account",
        account_type=credit_card_account_type,
        opening_balance=55.55,
        annual_rate=5.55,
        active=True,
        open_date=current_date(),
        statement_cycle_length=1,
        statement_cycle_period="m",
        credit_limit=55555,
        bank=bank,
        last_statement_amount=555.55,
        archive_balance=555.55,
        funding_account=None,
        calculate_payments=False,
        calculate_interest=False,
        payment_strategy="F",
        payment_amount=55.55,
        minimum_payment_amount=25.00,
        statement_day=15,
        due_day=15,
        pay_day=15,
    )
