import pytest

AUTH = {"Authorization": "Bearer test-api-key"}


# The graph endpoints now use per-user UserDashboardConfig (DEFAULT_GRAPH_WIDGETS
# when no real user is present) rather than the global Option singleton.
# DEFAULT_GRAPH_WIDGETS: widget 1 = "Expenses" (type 1), 2 = "Income" (type 2),
#                        3 = "Untagged" (type 3)


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_new_returns_list(api_client):
    """The /new endpoint must return a list (may be empty when no transactions exist)."""
    response = api_client.get("/tags/graph-by-tags/new?widget_id=1", headers=AUTH)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_new_widget2(api_client):
    response = api_client.get("/tags/graph-by-tags/new?widget_id=2", headers=AUTH)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_new_widget3(api_client):
    response = api_client.get("/tags/graph-by-tags/new?widget_id=3", headers=AUTH)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_returns_structure(api_client):
    """The /get endpoint must return labels and datasets with the default widget name."""
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
    # Label comes from DEFAULT_GRAPH_WIDGETS, not the Option singleton
    assert dataset["label"] == "Expenses"


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_widget2(api_client):
    response = api_client.get("/tags/graph-by-tags/get?widget_id=2", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "datasets" in data


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_widget3_untagged_path(api_client):
    """Widget 3 uses type_id=3 (all transactions), exercises the untagged path."""
    response = api_client.get("/tags/graph-by-tags/get?widget_id=3", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["labels"], list)
    assert isinstance(data["datasets"], list)


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_new_unknown_widget_falls_back(api_client):
    """Unknown widget_id falls back to type_id=1 defaults and returns a valid list."""
    response = api_client.get("/tags/graph-by-tags/new?widget_id=99", headers=AUTH)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.django_db
@pytest.mark.api
def test_get_graph_unknown_widget_falls_back(api_client):
    """Unknown widget_id falls back to type_id=1 defaults and returns valid graph shape."""
    response = api_client.get("/tags/graph-by-tags/get?widget_id=99", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "datasets" in data
