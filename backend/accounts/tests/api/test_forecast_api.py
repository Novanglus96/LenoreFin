import pytest


@pytest.mark.django_db
@pytest.mark.api
def test_get_forecast_returns_structure(api_client, test_checking_account):
    response = api_client.get(
        f"/accounts/forecast/get/{test_checking_account.id}"
        "?start_interval=7&end_interval=7",
        headers={"Authorization": "Bearer test-api-key"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "datasets" in data
    assert isinstance(data["labels"], list)
    assert len(data["labels"]) == 15  # 7 past + today + 7 future
    assert len(data["datasets"]) == 1
    dataset = data["datasets"][0]
    assert "data" in dataset
    assert len(dataset["data"]) == 15


@pytest.mark.django_db
@pytest.mark.api
def test_get_forecast_zero_interval(api_client, test_checking_account):
    response = api_client.get(
        f"/accounts/forecast/get/{test_checking_account.id}"
        "?start_interval=0&end_interval=0",
        headers={"Authorization": "Bearer test-api-key"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "datasets" in data
    assert len(data["labels"]) == 1  # today only


@pytest.mark.django_db
@pytest.mark.api
def test_get_forecast_nonexistent_account(api_client):
    response = api_client.get(
        "/accounts/forecast/get/9999?start_interval=7&end_interval=7",
        headers={"Authorization": "Bearer test-api-key"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "datasets" in data
