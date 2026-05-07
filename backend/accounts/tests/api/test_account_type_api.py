import pytest


@pytest.mark.django_db
@pytest.mark.api
def test_create_account_type(api_client):
    response = api_client.post(
        "/accounts/account-types/create",
        json={
            "account_type": "Checking",
            "color": "#FFFFFF",
            "icon": "some-icon",
        },
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    assert "id" in response.json()

    from accounts.models import AccountType

    assert AccountType.objects.filter(account_type="Checking").exists()


@pytest.mark.django_db
@pytest.mark.api
def test_create_account_type_duplicate(api_client, checking_account_type):
    response = api_client.post(
        "/accounts/account-types/create",
        json={
            "account_type": "Checking",
            "color": "#FFFFFF",
            "icon": "some-icon",
        },
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Account type already exists"


@pytest.mark.django_db
@pytest.mark.api
def test_get_account_type(api_client, checking_account_type):
    response = api_client.get(
        f"/accounts/account-types/get/{checking_account_type.id}",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    assert response.json()["account_type"] == checking_account_type.account_type


@pytest.mark.django_db
@pytest.mark.api
def test_account_type_list(
    api_client, checking_account_type, savings_account_type
):
    response = api_client.get(
        "/accounts/account-types/list",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["account_type"] == "Checking"
    assert data[1]["account_type"] == "Savings"


@pytest.mark.django_db
@pytest.mark.api
def test_account_type_update(api_client, checking_account_type):
    response = api_client.put(
        f"/accounts/account-types/update/{checking_account_type.id}",
        json={
            "account_type": "Updated Type",
            "color": "#FFFFFF",
            "icon": "some-icon",
        },
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    checking_account_type.refresh_from_db()
    assert checking_account_type.account_type == "Updated Type"


@pytest.mark.django_db
@pytest.mark.api
def test_delete_account_type(api_client, checking_account_type):
    response = api_client.delete(
        f"/accounts/account-types/delete/{checking_account_type.id}",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    from accounts.models import AccountType

    assert not AccountType.objects.filter(id=checking_account_type.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_get_account_type_not_found(api_client):
    response = api_client.get(
        "/accounts/account-types/get/9999",
        headers={
            "Authorization": "Bearer test-api-key",
        },
    )

    assert response.status_code == 404
