import pytest

AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_get_sub_tag(api_client, test_sub_tag):
    response = api_client.get(
        f"/tags/sub-tags/get/{test_sub_tag.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_sub_tag.id
    assert data["tag_name"] == test_sub_tag.tag_name


@pytest.mark.django_db
@pytest.mark.api
def test_get_sub_tag_not_found(api_client):
    response = api_client.get("/tags/sub-tags/get/9999", headers=AUTH)

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_list_sub_tags(api_client, test_sub_tag):
    response = api_client.get("/tags/sub-tags/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.django_db
@pytest.mark.api
def test_list_sub_tags_filter_by_tag_type(api_client, test_sub_tag, tag_type_expense):
    response = api_client.get(
        f"/tags/sub-tags/list?tag_type={tag_type_expense.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(t["tag_type"]["id"] == tag_type_expense.id for t in data)


@pytest.mark.django_db
@pytest.mark.api
def test_list_sub_tags_ordered_by_name(api_client, tag_type_expense):
    from tags.models import SubTag

    SubTag.objects.create(tag_name="Zebra Sub", tag_type=tag_type_expense)
    SubTag.objects.create(tag_name="Alpha Sub", tag_type=tag_type_expense)

    response = api_client.get("/tags/sub-tags/list", headers=AUTH)

    assert response.status_code == 200
    names = [item["tag_name"] for item in response.json()]
    assert names == sorted(names)


@pytest.mark.django_db
@pytest.mark.api
def test_sub_tag_schema_has_slug_and_is_system(api_client, test_sub_tag):
    response = api_client.get(
        f"/tags/sub-tags/get/{test_sub_tag.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert "slug" in data
    assert "is_system" in data
    assert data["slug"] == test_sub_tag.slug
    assert data["is_system"] == test_sub_tag.is_system
