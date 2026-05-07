import pytest


AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_create_tag_with_new_parent(api_client, tag_type_expense):
    response = api_client.post(
        "/tags/create",
        json={
            "parent_name": "New Main Tag",
            "parent_id": None,
            "child_id": None,
            "child_name": None,
            "tag_type_id": tag_type_expense.id,
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.django_db
@pytest.mark.api
def test_create_tag_with_existing_parent_and_new_child(
    api_client, test_main_tag, tag_type_expense
):
    response = api_client.post(
        "/tags/create",
        json={
            "parent_id": test_main_tag.id,
            "parent_name": None,
            "child_name": "New Sub Tag",
            "child_id": None,
            "tag_type_id": tag_type_expense.id,
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.django_db
@pytest.mark.api
def test_get_tag(api_client, test_tag):
    response = api_client.get(f"/tags/get/{test_tag.id}", headers=AUTH)

    assert response.status_code == 200
    assert response.json()["id"] == test_tag.id


@pytest.mark.django_db
@pytest.mark.api
def test_list_tags(api_client, test_tag):
    response = api_client.get("/tags/list", headers=AUTH)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


@pytest.mark.django_db
@pytest.mark.api
def test_list_tags_filter_by_type(api_client, test_tag, tag_type_expense):
    response = api_client.get(
        f"/tags/list?tag_type={tag_type_expense.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert all(t["tag_type"]["id"] == tag_type_expense.id for t in data)


@pytest.mark.django_db
@pytest.mark.api
def test_delete_tag(api_client, test_tag):
    response = api_client.delete(f"/tags/delete/{test_tag.id}", headers=AUTH)

    assert response.status_code == 200
    assert response.json()["success"] is True

    from tags.models import Tag
    assert not Tag.objects.filter(id=test_tag.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_update_tag(api_client, test_tag, tag_type_expense):
    response = api_client.put(
        f"/tags/update/{test_tag.id}",
        json={
            "parent_id": test_tag.parent.id,
            "parent_name": None,
            "child_id": test_tag.child.id if test_tag.child else None,
            "child_name": None,
            "tag_type_id": tag_type_expense.id,
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.django_db
@pytest.mark.api
def test_update_tag_not_found(api_client, tag_type_expense):
    response = api_client.put(
        "/tags/update/9999",
        json={
            "parent_id": None,
            "parent_name": None,
            "child_id": None,
            "child_name": None,
            "tag_type_id": tag_type_expense.id,
        },
        headers=AUTH,
    )

    assert response.status_code == 404
