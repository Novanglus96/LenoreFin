import pytest


@pytest.mark.django_db
def test_create_bank(api_client):
    response = api_client.post(
        "/accounts/banks/create",
        json={"bank_name": "Chase"},
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    assert "id" in response.json()

    from accounts.models import Bank

    assert Bank.objects.filter(bank_name="Chase").exists()


@pytest.mark.django_db
def test_create_bank_duplicate(api_client, bank):
    response = api_client.post(
        "/accounts/banks/create",
        json={"bank_name": bank.bank_name},
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Bank already exists"


@pytest.mark.django_db
def test_update_bank(api_client, bank):
    response = api_client.put(
        f"/accounts/banks/update/{bank.id}",
        json={"bank_name": "Updated Bank"},
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    bank.refresh_from_db()
    assert bank.bank_name == "Updated Bank"


@pytest.mark.django_db
def test_get_bank(api_client, bank):
    response = api_client.get(
        f"/accounts/banks/get/{bank.id}",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    assert response.json()["bank_name"] == bank.bank_name


@pytest.mark.django_db
def test_list_banks(api_client):
    from accounts.models import Bank

    Bank.objects.create(bank_name="Zeta")
    Bank.objects.create(bank_name="Alpha")

    response = api_client.get(
        "/accounts/banks/list",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["bank_name"] == "Alpha"
    assert data[1]["bank_name"] == "Zeta"


@pytest.mark.django_db
def test_delete_bank(api_client, bank):
    response = api_client.delete(
        f"/accounts/banks/delete/{bank.id}",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    from accounts.models import Bank

    assert not Bank.objects.filter(id=bank.id).exists()


@pytest.mark.django_db
def test_get_bank_not_found(api_client):
    response = api_client.get(
        "/accounts/banks/get/9999",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 404
