import pytest
from administration.models import GraphType, Option

AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.fixture
def graph_types():
    """Create the GraphType rows that Option FKs reference."""
    gt1 = GraphType.objects.create(id=1, graph_type="Type 1")
    gt2 = GraphType.objects.create(id=2, graph_type="Type 2")
    gt3 = GraphType.objects.create(id=3, graph_type="Type 3")
    return gt1, gt2, gt3


@pytest.fixture
def option_singleton(graph_types):
    """Create the singleton Option row required by the graph_by_tags endpoints."""
    return Option.objects.create(
        widget1_graph_name="Widget 1",
        widget1_month=0,
        widget1_exclude="[0]",
        widget1_type_id=1,
        widget2_graph_name="Widget 2",
        widget2_month=0,
        widget2_exclude="[0]",
        widget2_type_id=2,
        widget3_graph_name="Widget 3",
        widget3_month=0,
        widget3_exclude="[0]",
        widget3_type_id=3,
    )


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_new_returns_list(api_client, option_singleton):
    """The /new endpoint must return a list of pie graph items."""
    response = api_client.get("/tags/graph-by-tags/new?widget_id=1", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Each item must have the expected shape
    first = data[0]
    assert "key" in first
    assert "title" in first
    assert "value" in first
    assert "color" in first


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_new_widget2(api_client, option_singleton):
    response = api_client.get("/tags/graph-by-tags/new?widget_id=2", headers=AUTH)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_new_widget3(api_client, option_singleton):
    response = api_client.get("/tags/graph-by-tags/new?widget_id=3", headers=AUTH)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_returns_structure(api_client, option_singleton):
    """The /get endpoint must return labels and datasets."""
    response = api_client.get("/tags/graph-by-tags/get?widget_id=1", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "datasets" in data
    assert isinstance(data["labels"], list)
    assert isinstance(data["datasets"], list)
    assert len(data["datasets"]) == 1

    dataset = data["datasets"][0]
    assert "label" in dataset
    assert "data" in dataset
    assert "backgroundColor" in dataset
    assert dataset["label"] == "Widget 1"


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_widget2(api_client, option_singleton):
    response = api_client.get("/tags/graph-by-tags/get?widget_id=2", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "datasets" in data


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_widget3_untagged_path(api_client, option_singleton):
    """Widget 3 uses type_id=3 (all transactions), exercises the untagged path."""
    response = api_client.get("/tags/graph-by-tags/get?widget_id=3", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["labels"], list)
    assert isinstance(data["datasets"], list)


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_new_no_option_returns_error(api_client):
    """When there is no Option row the endpoint should return a 500."""
    response = api_client.get("/tags/graph-by-tags/new?widget_id=1", headers=AUTH)

    assert response.status_code == 500


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_no_option_returns_error(api_client):
    """When there is no Option row the endpoint should return a 500."""
    response = api_client.get("/tags/graph-by-tags/get?widget_id=1", headers=AUTH)

    assert response.status_code == 500
