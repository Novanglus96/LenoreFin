"""The savings plan over HTTP.

The engine is exercised in depth by the service tests; what these check is the
part only the endpoint can get wrong — that a plan with no funding account
answers instead of raising, that the three capacity figures and the bridging
schedule survive serialisation, and that the fields the widget reads are
actually in the payload.
"""

import pytest

AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_savings_plan_answers_when_there_is_nothing_to_plan(api_client):
    """No buckets, no funding account, no pay calendar.

    A fresh install hits this on the first page load, so it has to come back as
    a plan that explains itself rather than a 500.
    """
    response = api_client.get("/planning/savings-plan/get", headers=AUTH)

    assert response.status_code == 200
    plan = response.json()
    assert plan["feasible"] is False
    assert plan["lines"] == []
    assert plan["notes"]


@pytest.mark.django_db
@pytest.mark.api
def test_savings_plan_reports_all_three_capacity_figures(api_client):
    response = api_client.get("/planning/savings-plan/get", headers=AUTH)

    plan = response.json()
    # Each answers a different question, and the widget shows all three: what
    # the plan allocates to, what needs no bridging, what the year affords.
    assert "capacity_per_paycheck" in plan
    assert "path_capacity_per_paycheck" in plan
    assert "horizon_capacity_per_paycheck" in plan
    assert "bridges" in plan
    assert "breaches" in plan


@pytest.mark.django_db
@pytest.mark.api
def test_savings_plan_takes_a_horizon(api_client):
    response = api_client.get(
        "/planning/savings-plan/get?horizon_months=6", headers=AUTH
    )

    assert response.status_code == 200
    assert response.json()["horizon_months"] == 6
