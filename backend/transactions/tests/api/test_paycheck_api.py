import pytest
from transactions.models import Paycheck

AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_create_paycheck(api_client, test_payee):
    payload = {
        "gross": "5000.00",
        "net": "3800.00",
        "taxes": "800.00",
        "health": "150.00",
        "pension": "100.00",
        "fsa": "50.00",
        "dca": "25.00",
        "union_dues": "20.00",
        "four_fifty_seven_b": "55.00",
        "payee_id": test_payee.id,
    }

    response = api_client.post(
        "/transactions/paychecks/create",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert Paycheck.objects.filter(id=data["id"]).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_get_paycheck(api_client, test_paycheck):
    response = api_client.get(
        f"/transactions/paychecks/get/{test_paycheck.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_paycheck.id
    assert "gross" in data
    assert "payee" in data


@pytest.mark.django_db
@pytest.mark.api
def test_get_paycheck_not_found(api_client):
    response = api_client.get(
        "/transactions/paychecks/get/9999",
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_list_paychecks(api_client, test_paycheck):
    response = api_client.get(
        "/transactions/paychecks/list",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    ids = [item["id"] for item in data]
    assert test_paycheck.id in ids


@pytest.mark.django_db
@pytest.mark.api
def test_update_paycheck(api_client, test_paycheck, test_payee):
    payload = {
        "gross": "6000.00",
        "net": "4500.00",
        "taxes": "900.00",
        "health": "200.00",
        "pension": "150.00",
        "fsa": "75.00",
        "dca": "30.00",
        "union_dues": "25.00",
        "four_fifty_seven_b": "120.00",
        "payee_id": test_payee.id,
    }

    response = api_client.put(
        f"/transactions/paychecks/update/{test_paycheck.id}",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    test_paycheck.refresh_from_db()
    from decimal import Decimal
    assert test_paycheck.gross == Decimal("6000.00")
    assert test_paycheck.net == Decimal("4500.00")


@pytest.mark.django_db
@pytest.mark.api
def test_update_paycheck_not_found(api_client, test_payee):
    payload = {
        "gross": "1.00",
        "net": "1.00",
        "taxes": "1.00",
        "health": "1.00",
        "pension": "1.00",
        "fsa": "1.00",
        "dca": "1.00",
        "union_dues": "1.00",
        "four_fifty_seven_b": "1.00",
        "payee_id": test_payee.id,
    }

    response = api_client.put(
        "/transactions/paychecks/update/9999",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_delete_paycheck(api_client, test_paycheck):
    paycheck_id = test_paycheck.id

    response = api_client.delete(
        f"/transactions/paychecks/delete/{paycheck_id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert not Paycheck.objects.filter(id=paycheck_id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_delete_paycheck_not_found(api_client):
    response = api_client.delete(
        "/transactions/paychecks/delete/9999",
        headers=AUTH,
    )

    assert response.status_code == 404
