import pytest


AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_create_payee(api_client):
    response = api_client.post(
        "/administration/payees/create",
        json={"payee_name": "Test Payee API"},
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "id" in response.json()

    from administration.models import Payee
    assert Payee.objects.filter(payee_name="Test Payee API").exists()


@pytest.mark.django_db
@pytest.mark.api
def test_create_payee_duplicate(api_client, test_payee):
    response = api_client.post(
        "/administration/payees/create",
        json={"payee_name": test_payee.payee_name},
        headers=AUTH,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Payee already exists"


@pytest.mark.django_db
@pytest.mark.api
def test_get_payee(api_client, test_payee):
    response = api_client.get(
        f"/administration/payees/get/{test_payee.id}", headers=AUTH
    )

    assert response.status_code == 200
    assert response.json()["payee_name"] == test_payee.payee_name


@pytest.mark.django_db
@pytest.mark.api
def test_list_payees(api_client, test_payee):
    response = api_client.get("/administration/payees/list", headers=AUTH)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


@pytest.mark.django_db
@pytest.mark.api
def test_update_payee(api_client, test_payee):
    response = api_client.put(
        f"/administration/payees/update/{test_payee.id}",
        json={"payee_name": "Updated Payee"},
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    test_payee.refresh_from_db()
    assert test_payee.payee_name == "Updated Payee"


@pytest.mark.django_db
@pytest.mark.api
def test_delete_payee(api_client, test_payee):
    response = api_client.delete(
        f"/administration/payees/delete/{test_payee.id}", headers=AUTH
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    from administration.models import Payee
    assert not Payee.objects.filter(id=test_payee.id).exists()
