import pytest

AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_get_main_tag(api_client, test_main_tag):
    response = api_client.get(
        f"/tags/main-tags/get/{test_main_tag.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_main_tag.id
    assert data["tag_name"] == test_main_tag.tag_name


@pytest.mark.django_db
@pytest.mark.api
def test_get_main_tag_not_found(api_client):
    response = api_client.get("/tags/main-tags/get/9999", headers=AUTH)

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_list_main_tags(api_client, test_main_tag):
    response = api_client.get("/tags/main-tags/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.django_db
@pytest.mark.api
def test_list_main_tags_filter_by_tag_type(api_client, test_main_tag, tag_type_expense):
    response = api_client.get(
        f"/tags/main-tags/list?tag_type={tag_type_expense.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(t["tag_type"]["id"] == tag_type_expense.id for t in data)


@pytest.mark.django_db
@pytest.mark.api
def test_list_main_tags_empty_when_no_tags(api_client, tag_type_expense):
    response = api_client.get("/tags/main-tags/list", headers=AUTH)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.django_db
@pytest.mark.api
def test_list_main_tags_ordered_by_name(api_client, tag_type_expense):
    from tags.models import MainTag

    MainTag.objects.create(tag_name="Zebra Tag", tag_type=tag_type_expense)
    MainTag.objects.create(tag_name="Alpha Tag", tag_type=tag_type_expense)

    response = api_client.get("/tags/main-tags/list", headers=AUTH)

    assert response.status_code == 200
    names = [item["tag_name"] for item in response.json()]
    assert names == sorted(names)
