import pytest
from django.utils import timezone
import pytz
import os


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    return today.astimezone(tz_timezone).date()


AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_get_transaction(api_client, test_transaction):
    response = api_client.get(
        f"/transactions/get/{test_transaction.id}", headers=AUTH
    )

    assert response.status_code == 200
    assert response.json()["id"] == test_transaction.id


@pytest.mark.django_db
@pytest.mark.api
def test_get_transaction_not_found(api_client):
    response = api_client.get("/transactions/get/9999", headers=AUTH)

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_delete_transaction(api_client, test_transaction):
    response = api_client.patch(
        "/transactions/delete",
        json={"transactions": [test_transaction.id]},
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    from transactions.models import Transaction
    assert not Transaction.objects.filter(id=test_transaction.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_multiedit_transactions(api_client, test_transaction):
    new_date = current_date().isoformat()
    response = api_client.patch(
        "/transactions/multiedit",
        json={
            "transaction_ids": [test_transaction.id],
            "new_date": new_date,
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.django_db
@pytest.mark.api
def test_clear_transaction(api_client, test_transaction, test_cleared_transaction_status):
    response = api_client.patch(
        "/transactions/clear",
        json={"transactions": [test_transaction.id]},
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
