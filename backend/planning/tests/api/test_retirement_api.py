import pytest


AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_get_retirement_forecast_returns_structure(api_client):
    response = api_client.get("/planning/retirement/get", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "datasets" in data
    assert isinstance(data["labels"], list)
    assert isinstance(data["datasets"], list)
    # Total dataset always present even with no retirement accounts
    assert len(data["datasets"]) >= 1
    assert data["datasets"][0]["label"] == "Total"
