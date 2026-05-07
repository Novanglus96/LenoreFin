import pytest
from administration.models import Version


AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_get_version(api_client):
    Version.objects.create(version_number="1.2.3")

    response = api_client.get(
        "/administration/version/list",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["version_number"] == "1.2.3"
    assert "id" in data


@pytest.mark.django_db
@pytest.mark.api
def test_get_version_not_found(api_client):
    # No Version record with id=1 exists — should 404
    response = api_client.get(
        "/administration/version/list",
        headers=AUTH,
    )

    assert response.status_code == 404
