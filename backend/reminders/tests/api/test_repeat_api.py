import pytest

AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_get_repeat(api_client, test_repeat):
    response = api_client.get(
        f"/reminders/repeat/get/{test_repeat.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_repeat.id
    assert data["repeat_name"] == test_repeat.repeat_name


@pytest.mark.django_db
@pytest.mark.api
def test_list_repeats(api_client, test_repeat):
    response = api_client.get("/reminders/repeat/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    ids = [item["id"] for item in data]
    assert test_repeat.id in ids


@pytest.mark.django_db
@pytest.mark.api
def test_repeat_schema_has_slug_and_is_system(api_client, test_repeat):
    response = api_client.get(
        f"/reminders/repeat/get/{test_repeat.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert "slug" in data
    assert "is_system" in data
    assert data["slug"] == test_repeat.slug
    assert data["is_system"] == test_repeat.is_system
