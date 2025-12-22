import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
import pytz
import os
from accounts.models import Account


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.mark.django_db
@pytest.mark.unit
def test_account_creation(bank, checking_account_type, test_checking_account):
    account = test_checking_account

    assert account.id is not None
    assert account.account_name == "Test Checking Account"
    assert account.account_type == checking_account_type
    assert account.opening_balance == 55.55
    assert account.annual_rate == 5.55
    assert account.active
    assert account.open_date == current_date()
    assert account.statement_cycle_length == 1
    assert account.statement_cycle_period == "m"
    assert account.credit_limit == 55555
    assert account.bank == bank
    assert account.last_statement_amount == 555.55
    assert account.archive_balance == 555.55
    assert account.funding_account is None
    assert not account.calculate_payments
    assert not account.calculate_interest
    assert account.payment_strategy == "F"
    assert account.payment_amount == 55.55
    assert account.minimum_payment_amount == 25.00
    assert account.statement_day == 15
    assert account.due_day == 15
    assert account.pay_day == 15


@pytest.mark.django_db
@pytest.mark.unit
def test_account_creation_defaults(bank, checking_account_type):
    account = Account.objects.create(
        account_name="Test Checking Account",
        account_type=checking_account_type,
        bank=bank,
    )

    assert account.opening_balance == 0.00
    assert account.annual_rate == 0.00
    assert account.active
    assert account.open_date == current_date()
    assert account.statement_cycle_length == 0
    assert account.statement_cycle_period == "d"
    assert account.credit_limit == 0.00
    assert account.last_statement_amount == 0.00
    assert account.archive_balance == 0.00
    assert account.funding_account is None
    assert not account.calculate_payments
    assert not account.calculate_interest
    assert account.payment_strategy == "F"
    assert account.payment_amount == 0.00
    assert account.minimum_payment_amount == 0.00
    assert account.statement_day == 15
    assert account.due_day == 15
    assert account.pay_day == 15


@pytest.mark.django_db
@pytest.mark.unit
def test_account_str(test_checking_account):
    expected = "Test Checking Account"
    assert str(test_checking_account) == expected


@pytest.mark.django_db
@pytest.mark.unit
def test_foreign_key_bank_cascade(test_checking_account, bank):
    assert Account.objects.count() == 1

    bank.delete()

    assert Account.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.unit
def test_account_cannot_fund_itself(test_checking_account):
    account = test_checking_account

    # Set funding_account to itself
    account.funding_account = account

    with pytest.raises(ValidationError) as exc:
        account.full_clean()

    assert "cannot be its own funding account" in str(exc.value)


@pytest.mark.django_db
@pytest.mark.unit
def test_funding_account_must_be_checking(
    test_credit_card_account, test_savings_account
):
    test_credit_card_account.funding_account = test_savings_account

    with pytest.raises(ValidationError) as exc:
        test_credit_card_account.full_clean()

    assert "must be a checking account" in str(exc.value)


@pytest.mark.django_db
@pytest.mark.unit
def test_only_credit_cards_can_have_funding_account(
    test_savings_account, test_checking_account
):
    test_savings_account.funding_account = test_checking_account

    with pytest.raises(ValidationError) as exc:
        test_savings_account.full_clean()

    assert "can only be set for Credit Card accounts" in str(exc.value)
