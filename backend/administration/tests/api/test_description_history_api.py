import pytest
from administration.models import DescriptionHistory


AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_list_description_histories_empty(api_client):
    response = api_client.get(
        "/administration/description-histories/list",
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
@pytest.mark.api
def test_list_description_histories(api_client):
    DescriptionHistory.objects.create(
        description_normalized="walmart",
        description_pretty="Walmart",
    )
    DescriptionHistory.objects.create(
        description_normalized="amazon",
        description_pretty="Amazon",
    )

    response = api_client.get(
        "/administration/description-histories/list",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.django_db
@pytest.mark.api
def test_list_description_histories_ordered_alphabetically(api_client):
    DescriptionHistory.objects.create(
        description_normalized="zebra",
        description_pretty="Zebra",
    )
    DescriptionHistory.objects.create(
        description_normalized="apple",
        description_pretty="Apple",
    )
    DescriptionHistory.objects.create(
        description_normalized="mango",
        description_pretty="Mango",
    )

    response = api_client.get(
        "/administration/description-histories/list",
        headers=AUTH,
    )

    assert response.status_code == 200
    descriptions = [item["description_pretty"] for item in response.json()]
    assert descriptions == sorted(descriptions)


@pytest.mark.django_db
@pytest.mark.api
def test_list_description_histories_includes_tag_field(api_client):
    DescriptionHistory.objects.create(
        description_normalized="costco",
        description_pretty="Costco",
        tag=None,
    )

    response = api_client.get(
        "/administration/description-histories/list",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "tag" in data[0]
    assert data[0]["tag"] is None
