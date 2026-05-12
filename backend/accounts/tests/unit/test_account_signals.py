import pytest
from unittest.mock import patch, call
from accounts.models import Account
from transactions.models import ForecastCacheTransaction
from django.db.models import Q
from django.utils import timezone
import pytz
import os
from core.cache.keys import (
    account_forecast_transactions,
    account_combined_transactions,
    account_cleared_balance,
    account_financials,
    account_pending_balance,
    account_all,
)


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.mark.django_db
@pytest.mark.unit
@patch("accounts.signals.async_task")
def test_new_account_triggers_cache_update(
    mock_async_task, credit_card_account_type, bank
):
    account = Account.objects.create(
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
        statement_balance=555.55,
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
    mock_async_task.assert_called_once_with(
        "transactions.tasks.update_cc_forecast_cache",
        account.id,
    )


@pytest.mark.django_db
@pytest.mark.unit
@patch("accounts.signals.async_task")
def test_relevant_change_triggers_cache_update(
    mock_async_task, test_credit_card_account
):
    test_credit_card_account.opening_balance = 500
    test_credit_card_account.save()

    mock_async_task.assert_called_once()


@pytest.mark.django_db
@pytest.mark.unit
@patch("accounts.signals.async_task")
def test_irrelevant_change_does_not_trigger_update(
    mock_async_task, test_credit_card_account
):
    mock_async_task.reset_mock()
    test_credit_card_account.account_name = "New Name"
    test_credit_card_account.save()

    mock_async_task.assert_not_called()


@pytest.mark.django_db
@pytest.mark.unit
@patch("accounts.signals.async_task")
def test_non_credit_account_does_not_trigger_update(
    mock_async_task, test_checking_account
):
    test_checking_account.opening_balance = 500
    test_checking_account.save()

    mock_async_task.assert_not_called()


@pytest.mark.django_db
@pytest.mark.unit
def test_account_delete_removes_forecast_cache(
    test_credit_card_account,
    test_checking_account,
    test_pending_transaction_status,
    test_expense_transaction_type,
):
    ForecastCacheTransaction.objects.create(
        source_account=test_credit_card_account,
        total_amount=100,
        status=test_pending_transaction_status,
        description="Description",
        transaction_type=test_expense_transaction_type,
    )

    ForecastCacheTransaction.objects.create(
        source_account=test_checking_account,
        destination_account=test_credit_card_account,
        total_amount=50,
        status=test_pending_transaction_status,
        description="Description",
        transaction_type=test_expense_transaction_type,
    )

    account_id = test_credit_card_account.id
    test_credit_card_account.delete()

    assert not ForecastCacheTransaction.objects.filter(
        Q(source_account_id=account_id) | Q(destination_account_id=account_id)
    ).exists()


@pytest.mark.django_db
@patch("accounts.signals.delete_pattern")
def test_cc_account_save_invalidates_forecast_cache(
    mock_delete_pattern, credit_card_account_type, bank
):
    account = Account.objects.create(
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
        statement_balance=555.55,
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

    expected_calls = [
        call(account_forecast_transactions(account.id)),
    ]

    mock_delete_pattern.assert_has_calls(
        expected_calls,
        any_order=True,
    )


@pytest.mark.django_db
@patch("accounts.signals.delete_pattern")
def test_non_cc_account_save_does_not_invalidate_forecast_cache(
    mock_delete_pattern, checking_account_type, bank
):
    account = Account.objects.create(
        account_name="Test Credit Card Account",
        account_type=checking_account_type,
        opening_balance=55.55,
        annual_rate=5.55,
        active=True,
        open_date=current_date(),
        statement_cycle_length=1,
        statement_cycle_period="m",
        credit_limit=55555,
        bank=bank,
        statement_balance=555.55,
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

    expected_calls = [
        call(account_forecast_transactions(account.id)),
    ]

    for expcted_call in expected_calls:
        assert expcted_call not in mock_delete_pattern.mock_calls


@pytest.mark.django_db
@patch("accounts.signals.delete_pattern")
def test_account_save_invalidates_caches(
    mock_delete_pattern, checking_account_type, bank
):
    account = Account.objects.create(
        account_name="Test Credit Card Account",
        account_type=checking_account_type,
        opening_balance=55.55,
        annual_rate=5.55,
        active=True,
        open_date=current_date(),
        statement_cycle_length=1,
        statement_cycle_period="m",
        credit_limit=55555,
        bank=bank,
        statement_balance=555.55,
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

    expected_calls = [
        call(account_combined_transactions(account.id)),
        call(account_cleared_balance(account.id)),
        call(account_financials(account.id)),
        call(account_pending_balance(account.id)),
    ]

    mock_delete_pattern.assert_has_calls(
        expected_calls,
        any_order=True,
    )


@pytest.mark.django_db
@patch("accounts.signals.delete_pattern")
def test_account_delete_invalidates_all_cache(
    mock_delete_pattern, checking_account_type, bank
):
    account = Account.objects.create(
        account_name="Test Credit Card Account",
        account_type=checking_account_type,
        opening_balance=55.55,
        annual_rate=5.55,
        active=True,
        open_date=current_date(),
        statement_cycle_length=1,
        statement_cycle_period="m",
        credit_limit=55555,
        bank=bank,
        statement_balance=555.55,
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
    account_id = account.id
    account.delete()

    expected_calls = [
        call(account_all(account_id)),
    ]

    mock_delete_pattern.assert_has_calls(
        expected_calls,
        any_order=True,
    )
