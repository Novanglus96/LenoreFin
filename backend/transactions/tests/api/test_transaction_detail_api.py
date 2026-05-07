import pytest
from decimal import Decimal
from transactions.models import TransactionDetail

AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_create_transaction_detail(api_client, test_transaction, test_checking_account, test_tag):
    payload = {
        "transaction_id": test_transaction.id,
        "account_id": test_checking_account.id,
        "detail_amt": "25.00",
        "tag_id": test_tag.id,
        "full_toggle": False,
    }

    response = api_client.post(
        "/transactions/transaction-details/create",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert TransactionDetail.objects.filter(id=data["id"]).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_get_transaction_detail(api_client, test_transaction, test_tag):
    detail = TransactionDetail.objects.create(
        transaction=test_transaction,
        detail_amt=Decimal("10.00"),
        tag=test_tag,
        full_toggle=False,
    )

    response = api_client.get(
        f"/transactions/transaction-details/get/{detail.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == detail.id
    assert "detail_amt" in data
    assert "tag" in data


@pytest.mark.django_db
@pytest.mark.api
def test_get_transaction_detail_not_found(api_client):
    response = api_client.get(
        "/transactions/transaction-details/get/9999",
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_list_transaction_details(api_client, test_transaction, test_tag):
    detail = TransactionDetail.objects.create(
        transaction=test_transaction,
        detail_amt=Decimal("15.00"),
        tag=test_tag,
        full_toggle=False,
    )

    response = api_client.get(
        "/transactions/transaction-details/list",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    ids = [item["id"] for item in data]
    assert detail.id in ids


@pytest.mark.django_db
@pytest.mark.api
def test_update_transaction_detail(api_client, test_transaction, test_checking_account, test_tag):
    detail = TransactionDetail.objects.create(
        transaction=test_transaction,
        detail_amt=Decimal("10.00"),
        tag=test_tag,
        full_toggle=False,
    )

    payload = {
        "transaction_id": test_transaction.id,
        "account_id": test_checking_account.id,
        "detail_amt": "99.99",
        "tag_id": test_tag.id,
        "full_toggle": True,
    }

    response = api_client.put(
        f"/transactions/transaction-details/update/{detail.id}",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    detail.refresh_from_db()
    assert detail.detail_amt == Decimal("99.99")
    assert detail.full_toggle is True


@pytest.mark.django_db
@pytest.mark.api
def test_update_transaction_detail_not_found(api_client, test_transaction, test_checking_account, test_tag):
    payload = {
        "transaction_id": test_transaction.id,
        "account_id": test_checking_account.id,
        "detail_amt": "10.00",
        "tag_id": test_tag.id,
        "full_toggle": False,
    }

    response = api_client.put(
        "/transactions/transaction-details/update/9999",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_delete_transaction_detail(api_client, test_transaction, test_tag):
    detail = TransactionDetail.objects.create(
        transaction=test_transaction,
        detail_amt=Decimal("10.00"),
        tag=test_tag,
        full_toggle=False,
    )
    detail_id = detail.id

    response = api_client.delete(
        f"/transactions/transaction-details/delete/{detail_id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert not TransactionDetail.objects.filter(id=detail_id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_delete_transaction_detail_not_found(api_client):
    response = api_client.delete(
        "/transactions/transaction-details/delete/9999",
        headers=AUTH,
    )

    assert response.status_code == 404
