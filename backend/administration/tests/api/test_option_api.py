import pytest
from administration.models import Option


AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.fixture
def test_option():
    return Option.objects.create(
        alert_balance="100.00",
        alert_period=3,
        widget1_graph_name="Widget 1",
        widget1_exclude="",
        widget2_graph_name="Widget 2",
        widget2_exclude="",
        widget3_graph_name="Widget 3",
        widget3_exclude="",
        auto_archive=True,
        archive_length=2,
        enable_cc_bill_calculation=True,
    )


@pytest.mark.django_db
@pytest.mark.api
def test_get_option(api_client, test_option):
    response = api_client.get(
        f"/administration/options/get/{test_option.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_option.id
    assert data["alert_period"] == 3
    assert data["widget1_graph_name"] == "Widget 1"


@pytest.mark.django_db
@pytest.mark.api
def test_get_option_not_found(api_client):
    response = api_client.get(
        "/administration/options/get/99999",
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_list_options(api_client, test_option):
    response = api_client.get("/administration/options/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id"] == test_option.id


@pytest.mark.django_db
@pytest.mark.api
def test_update_option(api_client, test_option):
    payload = {
        "alert_period": 6,
        "widget1_graph_name": "Updated Widget 1",
        "widget2_graph_name": "Updated Widget 2",
        "widget3_graph_name": "Updated Widget 3",
    }
    response = api_client.patch(
        f"/administration/options/update/{test_option.id}",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    test_option.refresh_from_db()
    assert test_option.alert_period == 6
    assert test_option.widget1_graph_name == "Updated Widget 1"


@pytest.mark.django_db
@pytest.mark.api
def test_update_option_not_found(api_client):
    payload = {"alert_period": 1}
    response = api_client.patch(
        "/administration/options/update/99999",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_delete_option(api_client, test_option):
    response = api_client.delete(
        f"/administration/options/delete/{test_option.id}",
        headers=AUTH,
    )

    # Option is a SingletonModel — delete raises ValidationError, view returns 500
    assert response.status_code == 500
