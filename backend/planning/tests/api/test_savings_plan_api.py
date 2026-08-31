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


@pytest.mark.django_db
@pytest.mark.api
def test_every_plan_line_is_named(
    api_client,
    test_checking_account,
    test_savings_account,
    test_reminder,
    test_income_transaction_type,
    test_repeat,
    test_tag,
):
    """The widget's first column.

    A line carries the bucket's id and its name under separate keys, and the
    name is what a person reads — a table of amounts against blank rows is
    useless however right the arithmetic is. This is worth a test because
    getting it wrong is silent: the payload still validates, the totals are
    still correct, and the column just renders empty.
    """
    from datetime import timedelta

    from planning.models import Bucket
    from reminders.models import Reminder
    from utils.dates import get_todays_date_timezone_adjusted

    # Without a payday there is no pay calendar, and the plan short-circuits
    # to a note instead of a set of lines.
    Reminder.objects.create(
        tag=test_tag,
        amount=2000.00,
        # A source is required by the reminder-cache signal; only the
        # destination matters here, which is where the money lands.
        reminder_source_account=test_savings_account,
        reminder_destination_account=test_checking_account,
        description="Payday",
        transaction_type=test_income_transaction_type,
        repeat=test_repeat,
        next_date=get_todays_date_timezone_adjusted() + timedelta(days=7),
    )

    Bucket.objects.create(
        name="Grocery",
        contribution_per_paycheck="100.00",
        active=True,
        account=test_savings_account,
        reminder=test_reminder,
    )

    response = api_client.get("/planning/savings-plan/get", headers=AUTH)

    assert response.status_code == 200
    lines = response.json()["lines"]
    assert lines, "a bucket with an account and a reminder should produce a line"
    for line in lines:
        assert line["bucket_name"], f"line {line['bucket_id']} has no name"
    assert "Grocery" in [line["bucket_name"] for line in lines]
