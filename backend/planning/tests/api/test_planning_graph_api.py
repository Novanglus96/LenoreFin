import pytest

AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_planning_graph_pay_returns_list(api_client):
    """
    The /planning/graph/list?graph_type=pay endpoint should return a list of
    PlanningGraphList objects even when there are no paychecks in the database.
    """
    response = api_client.get(
        "/planning/graph/list?graph_type=pay", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Pay type always produces one top-level graph object (titled "Pay")
    assert len(data) == 1
    pay_report = data[0]
    assert pay_report["title"] == "Pay"
    assert "data" in pay_report
    assert isinstance(pay_report["data"], list)


@pytest.mark.django_db
@pytest.mark.api
def test_planning_graph_pay_sub_items_structure(api_client):
    """Each sub-graph in the pay report must have the required graph fields."""
    response = api_client.get(
        "/planning/graph/list?graph_type=pay", headers=AUTH
    )

    assert response.status_code == 200
    pay_report = response.json()[0]

    # There should be 9 pay fields (gross, net, taxes, health, pension, fsa, dca,
    # union_dues, four_fifty_seven_b)
    assert len(pay_report["data"]) == 9

    for item in pay_report["data"]:
        assert "data" in item
        assert "year1" in item
        assert "year2" in item
        assert "year1_avg" in item
        assert "year2_avg" in item
        assert "pretty_name" in item
        assert "key_name" in item

        graph_data = item["data"]
        assert "labels" in graph_data
        assert "datasets" in graph_data
        assert len(graph_data["labels"]) == 12
        assert len(graph_data["datasets"]) == 2


@pytest.mark.django_db
@pytest.mark.api
def test_planning_graph_expense_with_empty_option(api_client):
    """
    With no Option row configured the expense path should return 500.
    """
    response = api_client.get(
        "/planning/graph/list?graph_type=expense", headers=AUTH
    )

    # Without an Option row this will return 500 (get_object_or_404 raises 404
    # which is caught and re-raised as 500 inside the inner try/except).
    assert response.status_code in (404, 500)


@pytest.mark.django_db
@pytest.mark.api
def test_planning_graph_expense_with_option_no_tags(api_client):
    """
    When an Option row exists but report_main / report_individual are empty
    lists the endpoint should return an empty list of PlanningGraphList objects
    for the expense graph type.
    """
    from administration.models import Option

    Option.objects.create(
        widget1_graph_name="",
        widget1_month=0,
        widget1_exclude="[0]",
        widget2_graph_name="",
        widget2_month=0,
        widget2_exclude="[0]",
        widget3_graph_name="",
        widget3_month=0,
        widget3_exclude="[0]",
        report_main="[]",
        report_individual="[]",
        retirement_accounts="[]",
        christmas_accounts="[]",
        christmas_rewards="[]",
    )

    response = api_client.get(
        "/planning/graph/list?graph_type=expense", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # With empty tag lists there is one PlanningGraphList entry for "Main" with
    # no sub-graphs, plus zero individual reports.
    assert len(data) == 1
    assert data[0]["title"] == "Main"
    assert data[0]["data"] == []
