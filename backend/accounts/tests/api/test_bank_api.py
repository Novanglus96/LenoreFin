import pytest
from accounts.models import Bank


@pytest.mark.django_db
@pytest.mark.api
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
@pytest.mark.api
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
@pytest.mark.api
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
@pytest.mark.api
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
@pytest.mark.api
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
@pytest.mark.api
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
@pytest.mark.api
def test_get_bank_not_found(api_client):
    response = api_client.get(
        "/accounts/banks/get/9999",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 404


AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_create_bank_with_logo_url(api_client):
    response = api_client.post(
        "/accounts/banks/create",
        json={"bank_name": "Ally Financial", "logo_url": "https://icon.horse/icon/ally.com"},
        headers=AUTH,
    )

    assert response.status_code == 200
    bank = Bank.objects.get(bank_name="Ally Financial")
    assert bank.logo_url == "https://icon.horse/icon/ally.com"


@pytest.mark.django_db
@pytest.mark.api
def test_get_bank_includes_logo_url(api_client):
    bank = Bank.objects.create(
        bank_name="Ally Financial",
        logo_url="https://icon.horse/icon/ally.com",
    )

    response = api_client.get(f"/accounts/banks/get/{bank.id}", headers=AUTH)

    assert response.status_code == 200
    assert response.json()["logo_url"] == "https://icon.horse/icon/ally.com"


@pytest.mark.django_db
@pytest.mark.api
def test_update_bank_logo_url(api_client, bank):
    response = api_client.put(
        f"/accounts/banks/update/{bank.id}",
        json={"bank_name": bank.bank_name, "logo_url": "https://icon.horse/icon/testbank.com"},
        headers=AUTH,
    )

    assert response.status_code == 200
    bank.refresh_from_db()
    assert bank.logo_url == "https://icon.horse/icon/testbank.com"


@pytest.mark.django_db
@pytest.mark.api
def test_account_list_includes_bank_logo_url(api_client, test_checking_account):
    # Regression test: DomainBank DTO and mapper previously dropped logo_url
    test_checking_account.bank.logo_url = "https://icon.horse/icon/testbank.com"
    test_checking_account.bank.save()

    account_type_id = test_checking_account.account_type.id
    response = api_client.get(
        f"/accounts/list?account_type={account_type_id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    accounts = response.json()
    assert len(accounts) > 0
    assert accounts[0]["bank"]["logo_url"] == "https://icon.horse/icon/testbank.com"
