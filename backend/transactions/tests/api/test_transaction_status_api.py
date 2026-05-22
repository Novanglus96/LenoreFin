import pytest
from transactions.models import TransactionStatus

AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_get_transaction_status(api_client, test_pending_transaction_status):
    response = api_client.get(
        f"/transactions/transaction-statuses/get/{test_pending_transaction_status.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_pending_transaction_status.id
    assert data["transaction_status"] == "Pending"


@pytest.mark.django_db
@pytest.mark.api
def test_get_transaction_status_not_found(api_client):
    response = api_client.get(
        "/transactions/transaction-statuses/get/9999",
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_list_transaction_statuses(api_client, test_pending_transaction_status):
    response = api_client.get(
        "/transactions/transaction-statuses/list",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    ids = [item["id"] for item in data]
    assert test_pending_transaction_status.id in ids


@pytest.mark.django_db
@pytest.mark.api
def test_update_transaction_status(api_client, test_pending_transaction_status):
    payload = {"transaction_status": "Cleared"}

    response = api_client.put(
        f"/transactions/transaction-statuses/update/{test_pending_transaction_status.id}",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    test_pending_transaction_status.refresh_from_db()
    assert test_pending_transaction_status.transaction_status == "Cleared"


@pytest.mark.django_db
@pytest.mark.api
def test_update_transaction_status_not_found(api_client):
    payload = {"transaction_status": "NonExistent"}

    response = api_client.put(
        "/transactions/transaction-statuses/update/9999",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_update_transaction_status_duplicate(api_client, test_pending_transaction_status):
    """Updating a status to a name that already exists returns 400."""
    TransactionStatus.objects.create(transaction_status="Cleared")

    payload = {"transaction_status": "Cleared"}

    response = api_client.put(
        f"/transactions/transaction-statuses/update/{test_pending_transaction_status.id}",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.api
def test_delete_transaction_status(api_client, test_pending_transaction_status):
    status_id = test_pending_transaction_status.id

    response = api_client.delete(
        f"/transactions/transaction-statuses/delete/{status_id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert not TransactionStatus.objects.filter(id=status_id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_delete_transaction_status_not_found(api_client):
    response = api_client.delete(
        "/transactions/transaction-statuses/delete/9999",
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_transaction_status_schema_has_slug_and_is_system(api_client, test_pending_transaction_status):
    response = api_client.get(
        f"/transactions/transaction-statuses/get/{test_pending_transaction_status.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert "slug" in data
    assert "is_system" in data
    assert data["slug"] == test_pending_transaction_status.slug
    assert data["is_system"] == test_pending_transaction_status.is_system
