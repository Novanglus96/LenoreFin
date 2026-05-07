import pytest

AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_list_transactions_by_tag_returns_structure(api_client, test_tag):
    """
    Verify the /tag-graphs/list endpoint returns the expected schema shape
    even when there are no transactions for the tag.
    """
    response = api_client.get(
        f"/tags/tag-graphs/list?tag={test_tag.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()

    # Top-level keys
    assert "data" in data
    assert "year1" in data
    assert "year2" in data
    assert "year1_avg" in data
    assert "year2_avg" in data
    assert "transactions" in data

    # Graph data structure
    graph_data = data["data"]
    assert "labels" in graph_data
    assert "datasets" in graph_data
    assert len(graph_data["labels"]) == 12
    assert isinstance(graph_data["datasets"], list)
    assert len(graph_data["datasets"]) == 2

    # Datasets have this-year and last-year entries
    labels = [ds["label"] for ds in graph_data["datasets"]]
    assert len(labels) == 2

    # Averages are numeric
    assert isinstance(data["year1_avg"], (int, float))
    assert isinstance(data["year2_avg"], (int, float))

    # Transactions list is a list
    assert isinstance(data["transactions"], list)


@pytest.mark.django_db
@pytest.mark.api
def test_list_transactions_by_tag_year_values(api_client, test_tag):
    """year1 should be the current year and year2 should be year1 - 1."""
    from django.utils import timezone
    import pytz
    import os

    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    this_year = today_tz.year

    response = api_client.get(
        f"/tags/tag-graphs/list?tag={test_tag.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert data["year1"] == this_year
    assert data["year2"] == this_year - 1
