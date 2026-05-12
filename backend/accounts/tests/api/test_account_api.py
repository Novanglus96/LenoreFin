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
            "statement_balance": 555.55,
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
            "statement_balance": 555.55,
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


@pytest.mark.django_db
@pytest.mark.api
def test_update_account(api_client, test_checking_account):
    response = api_client.patch(
        f"/accounts/update/{test_checking_account.id}",
        json={"account_name": "Updated Account Name"},
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    test_checking_account.refresh_from_db()
    assert test_checking_account.account_name == "Updated Account Name"


@pytest.mark.django_db
@pytest.mark.api
def test_get_account(api_client, test_checking_account):
    response = api_client.get(
        f"/accounts/get/{test_checking_account.id}",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    assert response.json()["account_name"] == test_checking_account.account_name


@pytest.mark.django_db
@pytest.mark.api
def test_list_accounts_default_active(
    api_client,
    test_checking_account,
    test_savings_account,
    test_credit_card_account,
):
    test_credit_card_account.active = False
    test_credit_card_account.save()
    response = api_client.get(
        "/accounts/list",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["account_name"] == "Test Checking Account"
    assert data[1]["account_name"] == "Test Savings Account"


@pytest.mark.django_db
@pytest.mark.api
def test_list_accounts_with_inactive(
    api_client,
    test_checking_account,
    test_savings_account,
    test_credit_card_account,
):
    test_credit_card_account.active = False
    test_credit_card_account.save()
    response = api_client.get(
        "/accounts/list?inactive=true",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 3
    assert data[0]["account_name"] == "Test Checking Account"
    assert data[1]["account_name"] == "Test Savings Account"
    assert data[2]["account_name"] == "Test Credit Card Account"


@pytest.mark.django_db
@pytest.mark.api
def test_list_accounts_by_account_type(
    api_client,
    test_checking_account,
    test_savings_account,
    test_credit_card_account,
    checking_account_type,
):
    response = api_client.get(
        f"/accounts/list?account_type={checking_account_type.id}",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["account_name"] == "Test Checking Account"


@pytest.mark.django_db
@pytest.mark.api
def test_delete_account(api_client, test_checking_account):
    response = api_client.delete(
        f"/accounts/delete/{test_checking_account.id}",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    from accounts.models import Account

    assert not Account.objects.filter(id=test_checking_account.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_get_account_not_found(api_client):
    response = api_client.get(
        "/accounts/get/9999",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_account_type_in_account_response_has_slug_and_is_system(
    api_client, test_checking_account
):
    AUTH = {"Authorization": "Bearer test-api-key"}
    response = api_client.get(
        f"/accounts/get/{test_checking_account.id}", headers=AUTH
    )

    assert response.status_code == 200
    account_type = response.json()["account_type"]
    assert "slug" in account_type
    assert "is_system" in account_type
    assert account_type["slug"] == test_checking_account.account_type.slug
    assert account_type["is_system"] == test_checking_account.account_type.is_system
