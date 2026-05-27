import pytest
from django.utils import timezone
import pytz
import os
from datetime import timedelta


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


# --- Transaction filter tests ---

def _list(api_client, account_id, **extra):
    params = (
        f"view_type=1&account={account_id}&maxdays=14&forecast=false"
        f"&page=1&page_size=60"
    )
    for k, v in extra.items():
        params += f"&{k}={v}"
    return api_client.get(f"/transactions/list?{params}", headers=AUTH)


@pytest.mark.django_db
@pytest.mark.api
def test_filter_by_description_search(
    api_client, test_checking_account,
    test_pending_transaction_status, test_expense_transaction_type,
):
    from transactions.models import Transaction
    today = current_date()
    Transaction.objects.create(
        description="Groceries at Walmart",
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        transaction_date=today,
    )
    Transaction.objects.create(
        description="Netflix subscription",
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        transaction_date=today,
    )

    response = _list(api_client, test_checking_account.id, search="walmart")
    assert response.status_code == 200
    data = response.json()
    assert all("walmart" in t["description"].lower() for t in data["transactions"])
    assert data["total_records"] == 1


@pytest.mark.django_db
@pytest.mark.api
def test_filter_by_status(
    api_client, test_checking_account,
    test_pending_transaction_status, test_cleared_transaction_status,
    test_expense_transaction_type,
):
    from transactions.models import Transaction
    today = current_date()
    Transaction.objects.create(
        description="Pending tx",
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        transaction_date=today,
    )
    Transaction.objects.create(
        description="Cleared tx",
        status=test_cleared_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        transaction_date=today,
    )

    response = _list(api_client, test_checking_account.id, status_id=test_pending_transaction_status.id)
    assert response.status_code == 200
    data = response.json()
    assert all(t["status"]["id"] == test_pending_transaction_status.id for t in data["transactions"])
    assert data["total_records"] == 1


@pytest.mark.django_db
@pytest.mark.api
def test_filter_by_transaction_type(
    api_client, test_checking_account,
    test_pending_transaction_status,
    test_expense_transaction_type, test_income_transaction_type,
):
    from transactions.models import Transaction
    today = current_date()
    Transaction.objects.create(
        description="Expense",
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        transaction_date=today,
    )
    Transaction.objects.create(
        description="Income",
        status=test_pending_transaction_status,
        transaction_type=test_income_transaction_type,
        source_account=test_checking_account,
        transaction_date=today,
    )

    response = _list(api_client, test_checking_account.id, transaction_type_id=test_expense_transaction_type.id)
    assert response.status_code == 200
    data = response.json()
    assert all(t["transaction_type"]["id"] == test_expense_transaction_type.id for t in data["transactions"])
    assert data["total_records"] == 1


@pytest.mark.django_db
@pytest.mark.api
def test_filter_by_date_from(
    api_client, test_checking_account,
    test_pending_transaction_status, test_expense_transaction_type,
):
    from transactions.models import Transaction
    today = current_date()
    Transaction.objects.create(
        description="Old tx",
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        transaction_date=today - timedelta(days=5),
    )
    Transaction.objects.create(
        description="Recent tx",
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        transaction_date=today,
    )

    date_from = (today - timedelta(days=2)).isoformat()
    response = _list(api_client, test_checking_account.id, date_from=date_from)
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 1
    assert data["transactions"][0]["description"] == "Recent tx"


@pytest.mark.django_db
@pytest.mark.api
def test_filter_by_date_to(
    api_client, test_checking_account,
    test_pending_transaction_status, test_expense_transaction_type,
):
    from transactions.models import Transaction
    today = current_date()
    Transaction.objects.create(
        description="Old tx",
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        transaction_date=today - timedelta(days=5),
    )
    Transaction.objects.create(
        description="Recent tx",
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        transaction_date=today,
    )

    date_to = (today - timedelta(days=2)).isoformat()
    response = _list(api_client, test_checking_account.id, date_to=date_to)
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 1
    assert data["transactions"][0]["description"] == "Old tx"


@pytest.mark.django_db
@pytest.mark.api
def test_filter_no_results_returns_empty(
    api_client, test_checking_account,
    test_pending_transaction_status, test_expense_transaction_type,
):
    from transactions.models import Transaction
    today = current_date()
    Transaction.objects.create(
        description="Groceries",
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        transaction_date=today,
    )

    response = _list(api_client, test_checking_account.id, search="zzznomatch")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 0
    assert data["transactions"] == []
