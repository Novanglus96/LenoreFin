import pytest
from django.utils import timezone
import pytz
import os


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.mark.django_db
@pytest.mark.api
def test_create_account(api_client, bank, checking_account_type):
    response = api_client.post(
        "/accounts/create",
        json={
            "account_name": "Test Checking Account",
            "account_type_id": checking_account_type.id,
            "opening_balance": 55.55,
            "annual_rate": 5.55,
            "active": True,
            "open_date": current_date().isoformat(),
            "statement_cycle_length": 1,
            "statement_cycle_period": "m",
            "credit_limit": 55555,
            "bank_id": bank.id,
            "last_statement_amount": 555.55,
            "archive_balance": 555.55,
            "funding_account": None,
            "calculate_payments": False,
            "calculate_interest": False,
            "payment_strategy": "F",
            "payment_amount": 55.55,
            "minimum_payment_amount": 25.00,
            "statement_day": 15,
            "due_day": 15,
            "pay_day": 15,
        },
        headers={"Authorization": "Bearer test-api-key"},
    )

    assert response.status_code == 200
    assert "id" in response.json()

    from accounts.models import Account

    assert Account.objects.filter(account_name="Test Checking Account").exists()


@pytest.mark.django_db
@pytest.mark.api
def test_create_account_duplicate(
    api_client, bank, checking_account_type, test_checking_account
):
    response = api_client.post(
        "/accounts/create",
        json={
            "account_name": "Test Checking Account",
            "account_type_id": checking_account_type.id,
            "opening_balance": 55.55,
            "annual_rate": 5.55,
            "active": True,
            "open_date": current_date().isoformat(),
            "statement_cycle_length": 1,
            "statement_cycle_period": "m",
            "credit_limit": 55555,
            "bank_id": bank.id,
            "last_statement_amount": 555.55,
            "archive_balance": 555.55,
            "funding_account": None,
            "calculate_payments": False,
            "calculate_interest": False,
            "payment_strategy": "F",
            "payment_amount": 55.55,
            "minimum_payment_amount": 25.00,
            "statement_day": 15,
            "due_day": 15,
            "pay_day": 15,
        },
        headers={"Authorization": "Bearer test-api-key"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Account name already exists"
