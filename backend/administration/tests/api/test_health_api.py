import pytest


AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_health_check(api_client):
    response = api_client.get(
        "/administration/health/",
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.django_db
@pytest.mark.api
def test_health_check_no_auth(api_client):
    # Health endpoint is public — no auth required
    response = api_client.get("/administration/health/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
