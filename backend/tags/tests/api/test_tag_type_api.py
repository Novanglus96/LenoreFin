import pytest

AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_list_tag_types_returns_list(api_client, tag_type_expense):
    response = api_client.get("/tags/tag-types/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.django_db
@pytest.mark.api
def test_list_tag_types_excludes_id_3(api_client):
    from tags.models import TagType

    TagType.objects.create(id=3, tag_type="Misc")
    TagType.objects.create(tag_type="Expense")

    response = api_client.get("/tags/tag-types/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    ids = [item["id"] for item in data]
    assert 3 not in ids


@pytest.mark.django_db
@pytest.mark.api
def test_list_tag_types_ordered_by_id(api_client):
    from tags.models import TagType

    TagType.objects.create(tag_type="Expense")
    TagType.objects.create(tag_type="Income")

    response = api_client.get("/tags/tag-types/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    ids = [item["id"] for item in data]
    assert ids == sorted(ids)


@pytest.mark.django_db
@pytest.mark.api
def test_list_tag_types_empty_when_none(api_client):
    response = api_client.get("/tags/tag-types/list", headers=AUTH)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.django_db
@pytest.mark.api
def test_tag_type_schema_has_slug_and_is_system(api_client, tag_type_expense):
    response = api_client.get("/tags/tag-types/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    item = next(d for d in data if d["id"] == tag_type_expense.id)
    assert "slug" in item
    assert "is_system" in item
    assert item["slug"] == tag_type_expense.slug
    assert item["is_system"] == tag_type_expense.is_system
