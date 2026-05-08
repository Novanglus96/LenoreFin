import pytest
from unittest.mock import patch
from accounts.models import Bank, Account, AccountType
from tags.models import TagType, MainTag, SubTag, Tag
from transactions.models import (
    TransactionType,
    TransactionStatus,
    Paycheck,
    Transaction,
    ReminderCacheTransaction,
    ForecastCacheTransaction,
)
from administration.models import Payee
from reminders.models import Reminder, Repeat
from ninja.testing import TestClient
from backend.api import api
from django.utils import timezone
from django.contrib.auth.models import User, Group
import pytz
import os




@pytest.fixture(autouse=True)
def patch_delete_pattern():
    with patch("core.cache.helpers.delete_pattern", return_value=None), \
         patch("backend.utils.cache.delete_pattern", return_value=None), \
         patch("accounts.signals.delete_pattern", return_value=None), \
         patch("reminders.signals.delete_pattern", return_value=None), \
         patch("transactions.signals.delete_pattern", return_value=None), \
         patch("transactions.api.views.transaction.delete_pattern", return_value=None), \
         patch("transactions.tasks.delete_pattern", return_value=None):
        yield


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.fixture
def full_access_user(db):
    group, _ = Group.objects.get_or_create(name="Full Access")
    user, _ = User.objects.get_or_create(username="test_full_access")
    user.set_password("testpass")
    user.save()
    user.groups.set([group])
    return user


@pytest.fixture
def readonly_user(db):
    group, _ = Group.objects.get_or_create(name="Readonly")
    user, _ = User.objects.get_or_create(username="test_readonly")
    user.set_password("testpass")
    user.save()
    user.groups.set([group])
    return user


@pytest.fixture(scope="session")
def api_client():
    return TestClient(api)


@pytest.fixture(autouse=True)
def patch_auth_as_full_access():
    """Default all API test requests to an authenticated full-access user.

    Tests that need to verify 401/403 behaviour should override this via
    an explicit patch on administration.api.dependencies.auth.
    """
    from unittest.mock import Mock
    full_access_mock = Mock()
    full_access_mock.is_authenticated = True
    full_access_mock.groups.filter.return_value.exists.return_value = True

    with patch(
        "administration.api.dependencies.auth.SessionAuth.authenticate",
        return_value=full_access_mock,
    ), patch(
        "administration.api.dependencies.auth.FullAccessAuth.authenticate",
        return_value=full_access_mock,
    ):
        yield


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


@pytest.fixture
def test_expense_transaction_type():
    return TransactionType.objects.create(transaction_type="Expense")


@pytest.fixture
def test_pending_transaction_status():
    return TransactionStatus.objects.create(transaction_status="Pending")


@pytest.fixture
def test_cleared_transaction_status():
    return TransactionStatus.objects.create(transaction_status="Cleared")


@pytest.fixture
def test_payee():
    return Payee.objects.create(payee_name="Test Payee")


@pytest.fixture
def test_paycheck(test_payee):
    return Paycheck.objects.create(
        gross=1.00,
        net=1.00,
        taxes=1.00,
        health=1.00,
        pension=1.00,
        fsa=1.00,
        dca=1.00,
        union_dues=1.00,
        four_fifty_seven_b=1.00,
        payee=test_payee,
    )


@pytest.fixture
def test_transaction(
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_checking_account,
):
    return Transaction.objects.create(
        status=test_pending_transaction_status,
        description="Description",
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
    )


@pytest.fixture
def test_reminder_transaction(
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_checking_account,
    test_reminder,
):
    return ReminderCacheTransaction.objects.create(
        status=test_pending_transaction_status,
        description="Description",
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        reminder=test_reminder,
    )


@pytest.fixture
def test_forecast_transaction(
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_checking_account,
):
    return ForecastCacheTransaction.objects.create(
        status=test_pending_transaction_status,
        description="Description",
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
    )


@pytest.fixture
def test_repeat():
    return Repeat.objects.create(
        repeat_name="Test Repeat", days=1, weeks=1, months=1, years=1
    )


@pytest.fixture
def test_reminder(
    test_tag,
    test_checking_account,
    test_savings_account,
    test_expense_transaction_type,
    test_repeat,
):
    return Reminder.objects.create(
        tag=test_tag,
        amount=1.00,
        reminder_source_account=test_checking_account,
        reminder_destination_account=test_savings_account,
        description="Description",
        transaction_type=test_expense_transaction_type,
        repeat=test_repeat,
    )
