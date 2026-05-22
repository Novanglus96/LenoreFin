import pytest
from transactions.models import TransactionType

AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_get_transaction_type(api_client, test_expense_transaction_type):
    response = api_client.get(
        f"/transactions/transaction-types/get/{test_expense_transaction_type.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_expense_transaction_type.id
    assert data["transaction_type"] == "Expense"


@pytest.mark.django_db
@pytest.mark.api
def test_get_transaction_type_not_found(api_client):
    response = api_client.get(
        "/transactions/transaction-types/get/9999",
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_list_transaction_types(api_client, test_expense_transaction_type):
    response = api_client.get(
        "/transactions/transaction-types/list",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    ids = [item["id"] for item in data]
    assert test_expense_transaction_type.id in ids


@pytest.mark.django_db
@pytest.mark.api
def test_update_transaction_type(api_client, test_expense_transaction_type):
    payload = {"transaction_type": "Income"}

    response = api_client.put(
        f"/transactions/transaction-types/update/{test_expense_transaction_type.id}",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    test_expense_transaction_type.refresh_from_db()
    assert test_expense_transaction_type.transaction_type == "Income"


@pytest.mark.django_db
@pytest.mark.api
def test_update_transaction_type_not_found(api_client):
    payload = {"transaction_type": "Transfer"}

    response = api_client.put(
        "/transactions/transaction-types/update/9999",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_update_transaction_type_duplicate(api_client, test_expense_transaction_type):
    """Updating a type to a name that already exists returns 400."""
    TransactionType.objects.create(transaction_type="Income")

    payload = {"transaction_type": "Income"}

    response = api_client.put(
        f"/transactions/transaction-types/update/{test_expense_transaction_type.id}",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.api
def test_delete_transaction_type(api_client, test_expense_transaction_type):
    type_id = test_expense_transaction_type.id

    response = api_client.delete(
        f"/transactions/transaction-types/delete/{type_id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert not TransactionType.objects.filter(id=type_id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_delete_transaction_type_not_found(api_client):
    response = api_client.delete(
        "/transactions/transaction-types/delete/9999",
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_transaction_type_schema_has_slug_and_is_system(api_client, test_expense_transaction_type):
    response = api_client.get(
        f"/transactions/transaction-types/get/{test_expense_transaction_type.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert "slug" in data
    assert "is_system" in data
    assert data["slug"] == test_expense_transaction_type.slug
    assert data["is_system"] == test_expense_transaction_type.is_system
