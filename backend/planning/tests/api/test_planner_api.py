"""API tests for the financial planner endpoints.

The apply endpoint is the one with teeth — it writes to both the contribution
and its linked reminder — so most of the weight is there.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

AUTH = {"Authorization": "Bearer test-api-key"}


def _make_drain(account, status, ttype, months=6, amount=-100):
    from transactions.models import Transaction

    today = date.today()
    for i in range(months):
        Transaction.objects.create(
            transaction_date=today - timedelta(days=30 * (i + 1)),
            total_amount=Decimal(str(amount)),
            status=status,
            description="Drain",
            transaction_type=ttype,
            source_account=account,
        )


@pytest.fixture
def biweekly_repeat():
    from reminders.models import Repeat

    return Repeat.objects.create(
        repeat_name="Every 2 Weeks", days=0, weeks=2, months=0, years=0
    )


@pytest.fixture
def planned_contribution(
    test_savings_account,
    test_checking_account,
    test_cleared_transaction_status,
    test_expense_transaction_type,
    test_transfer_transaction_type,
    biweekly_repeat,
):
    """A draining account with a hold-steady goal and a linked reminder."""
    from planning.models import Contribution
    from reminders.models import Reminder

    _make_drain(
        test_savings_account,
        test_cleared_transaction_status,
        test_expense_transaction_type,
    )
    reminder = Reminder.objects.create(
        amount=Decimal("10.00"),
        reminder_source_account=test_checking_account,
        reminder_destination_account=test_savings_account,
        description="House Transfer",
        transaction_type=test_transfer_transaction_type,
        repeat=biweekly_repeat,
    )
    return Contribution.objects.create(
        contribution="House",
        per_paycheck=Decimal("10.00"),
        account=test_savings_account,
        reminder=reminder,
        goal_type=Contribution.GOAL_HOLD,
    )


@pytest.mark.django_db
@pytest.mark.api
def test_analysis_returns_row_with_trend_and_suggestion(
    api_client, planned_contribution
):
    response = api_client.get("/planning/planner/analysis", headers=AUTH)

    assert response.status_code == 200
    body = response.json()
    row = next(
        r for r in body["rows"] if r["contribution_id"] == planned_contribution.id
    )
    assert row["account_name"] == "Test Savings Account"
    assert row["goal_type"] == "hold"
    assert row["trend"] is not None
    assert Decimal(row["trend"]["natural_flow_per_month"]) < 0
    assert row["suggestion"] is not None
    # Must ask for more than the 10.00 currently going in.
    assert Decimal(row["suggestion"]["required_per_paycheck"]) > Decimal("10.00")
    assert Decimal(row["suggestion"]["delta_per_paycheck"]) > 0


@pytest.mark.django_db
@pytest.mark.api
def test_analysis_totals_reflect_suggestions(api_client, planned_contribution):
    response = api_client.get("/planning/planner/analysis", headers=AUTH)

    body = response.json()
    assert Decimal(body["current_per_paycheck_total"]) == Decimal("10.00")
    assert Decimal(body["suggested_per_paycheck_total"]) > Decimal("10.00")
    assert Decimal(body["delta_per_paycheck_total"]) == Decimal(
        body["suggested_per_paycheck_total"]
    ) - Decimal(body["current_per_paycheck_total"])


@pytest.mark.django_db
@pytest.mark.api
def test_analysis_rejects_absurd_window(api_client):
    assert api_client.get(
        "/planning/planner/analysis?months=0", headers=AUTH
    ).status_code == 400
    assert api_client.get(
        "/planning/planner/analysis?months=61", headers=AUTH
    ).status_code == 400


@pytest.mark.django_db
@pytest.mark.api
def test_analysis_row_for_contribution_without_account(api_client):
    """An unlinked contribution still appears, with a note instead of a trend."""
    from planning.models import Contribution

    c = Contribution.objects.create(
        contribution="Orphan", per_paycheck=Decimal("25.00")
    )

    body = api_client.get("/planning/planner/analysis", headers=AUTH).json()

    row = next(r for r in body["rows"] if r["contribution_id"] == c.id)
    assert row["trend"] is None
    assert row["suggestion"] is None
    assert "Link an account" in row["note"]
    # It still costs money, so it must count toward the total.
    assert Decimal(body["current_per_paycheck_total"]) == Decimal("25.00")


@pytest.mark.django_db
@pytest.mark.api
def test_goalless_contribution_shows_its_amount_and_counts_in_totals(
    api_client, planned_contribution
):
    """No goal means no suggestion — but the money is still going out.

    The row must report what is actually being contributed, and carry into both
    totals unchanged, so the paycheck figures stay truthful. Reading the amount
    off `suggestion` showed 0.00 for these rows and understated the totals.
    """
    from planning.models import Contribution

    planned_contribution.goal_type = Contribution.GOAL_NONE
    planned_contribution.save(update_fields=["goal_type"])

    body = api_client.get("/planning/planner/analysis", headers=AUTH).json()
    row = next(
        r for r in body["rows"] if r["contribution_id"] == planned_contribution.id
    )

    assert row["suggestion"] is None
    assert Decimal(row["current_per_paycheck"]) == Decimal("10.00")
    assert "No goal set" in row["note"]
    # Counted, and counted identically on both sides so the change reads zero.
    assert Decimal(body["current_per_paycheck_total"]) == Decimal("10.00")
    assert Decimal(body["suggested_per_paycheck_total"]) == Decimal("10.00")
    assert Decimal(body["delta_per_paycheck_total"]) == Decimal("0.00")


@pytest.mark.django_db
@pytest.mark.api
def test_apply_updates_contribution_and_reminder_together(
    api_client, planned_contribution
):
    """Both sides move, so the drift indicator resets instead of sticking."""
    from planning.models import Contribution
    from reminders.models import Reminder

    response = api_client.post(
        "/planning/planner/apply",
        json={"contribution_ids": [planned_contribution.id]},
        headers=AUTH,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["applied_count"] == 1
    result = body["results"][0]
    assert result["applied"] is True
    assert Decimal(result["previous_per_paycheck"]) == Decimal("10.00")

    new_amount = Decimal(result["new_per_paycheck"])
    contribution = Contribution.objects.get(pk=planned_contribution.id)
    reminder = Reminder.objects.get(pk=planned_contribution.reminder_id)
    assert contribution.per_paycheck == new_amount
    assert reminder.amount == new_amount


@pytest.mark.django_db
@pytest.mark.api
def test_apply_preserves_the_reminder_sign_convention(
    api_client, planned_contribution
):
    """A transfer reminder must stay negative after applying.

    Real reminders store transfers and expenses as negative amounts, with
    direction carried by source/destination rather than by sign, and the
    transaction generator copies `amount` straight into `total_amount`. Writing
    the solver's magnitude raw would flip the transfer positive and produce a
    transaction unlike every other one in the ledger.
    """
    from reminders.models import Reminder

    reminder = Reminder.objects.get(pk=planned_contribution.reminder_id)
    reminder.amount = Decimal("-10.00")
    reminder.save(update_fields=["amount"])

    response = api_client.post(
        "/planning/planner/apply",
        json={"contribution_ids": [planned_contribution.id]},
        headers=AUTH,
    )

    assert response.status_code == 200
    reminder.refresh_from_db()
    assert reminder.amount < 0, "transfer reminder flipped positive"
    new_amount = Decimal(response.json()["results"][0]["new_per_paycheck"])
    assert reminder.amount == -new_amount


@pytest.mark.django_db
@pytest.mark.api
def test_apply_leaves_no_drift_behind(api_client, planned_contribution):
    """After applying, the analysis must report zero drift for that row."""
    api_client.post(
        "/planning/planner/apply",
        json={"contribution_ids": [planned_contribution.id]},
        headers=AUTH,
    )

    body = api_client.get("/planning/planner/analysis", headers=AUTH).json()
    row = next(
        r for r in body["rows"] if r["contribution_id"] == planned_contribution.id
    )
    assert Decimal(row["drift"]) == Decimal("0.00")


@pytest.mark.django_db
@pytest.mark.api
def test_apply_reports_unknown_contribution_without_failing_batch(
    api_client, planned_contribution
):
    response = api_client.post(
        "/planning/planner/apply",
        json={"contribution_ids": [planned_contribution.id, 999999]},
        headers=AUTH,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["applied_count"] == 1
    missing = next(r for r in body["results"] if r["contribution_id"] == 999999)
    assert missing["applied"] is False
    assert "not found" in missing["reason"].lower()


@pytest.mark.django_db
@pytest.mark.api
def test_apply_skips_contribution_with_no_goal(api_client, test_savings_account):
    from planning.models import Contribution

    c = Contribution.objects.create(
        contribution="NoGoal",
        per_paycheck=Decimal("15.00"),
        account=test_savings_account,
    )

    body = api_client.post(
        "/planning/planner/apply",
        json={"contribution_ids": [c.id]},
        headers=AUTH,
    ).json()

    assert body["applied_count"] == 0
    assert body["results"][0]["applied"] is False
    # The planned figure must be left exactly as it was.
    assert Contribution.objects.get(pk=c.id).per_paycheck == Decimal("15.00")


@pytest.mark.django_db
@pytest.mark.api
def test_apply_rejects_empty_list(api_client):
    response = api_client.post(
        "/planning/planner/apply", json={"contribution_ids": []}, headers=AUTH
    )

    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.api
def test_projection_returns_two_diverging_curves(api_client, planned_contribution):
    response = api_client.get(
        f"/planning/planner/projection/{planned_contribution.id}?months=12",
        headers=AUTH,
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["points"]) == 13
    assert body["approximate"] is True
    first, last = body["points"][0], body["points"][-1]
    assert Decimal(first["balance_now"]) == Decimal(first["balance_if_applied"])
    # Applying the suggestion must beat doing nothing.
    assert Decimal(last["balance_if_applied"]) > Decimal(last["balance_now"])


@pytest.mark.django_db
@pytest.mark.api
def test_projection_404s_for_unknown_contribution(api_client):
    assert api_client.get(
        "/planning/planner/projection/999999", headers=AUTH
    ).status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_projection_400s_without_an_account(api_client):
    from planning.models import Contribution

    c = Contribution.objects.create(
        contribution="NoAcct", per_paycheck=Decimal("5.00")
    )

    assert api_client.get(
        f"/planning/planner/projection/{c.id}", headers=AUTH
    ).status_code == 400




@pytest.mark.django_db
@pytest.mark.api
def test_maximise_divides_allocatable_capacity(
    api_client, planned_contribution, test_savings_account
):
    """A maximise goal is the residual claimant on capacity, not on take-home.

    It cannot be solved per-account: the answer is defined by what the rest of
    the plan costs, so it runs as a second pass once the others are known.
    """
    from planning.models import Contribution

    college = Contribution.objects.create(
        contribution="College",
        per_paycheck=Decimal("5.00"),
        account=test_savings_account,
        goal_type=Contribution.GOAL_MAXIMISE,
    )

    body = api_client.get("/planning/planner/analysis", headers=AUTH).json()
    row = next(r for r in body["rows"] if r["contribution_id"] == college.id)
    other = next(
        r for r in body["rows"] if r["contribution_id"] == planned_contribution.id
    )

    assert row["suggestion"]["goal_type"] == "maximise"
    allocatable = Decimal(body["headroom"]["allocatable_per_paycheck"])
    expected = allocatable - Decimal(other["suggestion"]["required_per_paycheck"])
    if expected < 0:
        expected = Decimal("0")
    assert Decimal(row["suggestion"]["required_per_paycheck"]) == pytest.approx(
        expected, abs=Decimal("0.02")
    )


@pytest.mark.django_db
@pytest.mark.api
def test_headroom_is_reported_against_allocatable_not_take_home(
    api_client, planned_contribution
):
    """The page must quote capacity, and keep take-home only as context."""
    body = api_client.get("/planning/planner/analysis", headers=AUTH).json()
    h = body["headroom"]

    assert h["allocatable_per_paycheck"] is not None
    assert h["funding_account_drift"] is not None
    # Capacity is today's allocation adjusted by drift — not take-home, which
    # for a hub account overstates it by hundreds a paycheck.
    # Capacity is measured against *effective* funding — scheduled plus the
    # top-ups happening by hand — not the scheduled figure alone.
    assert Decimal(h["allocatable_per_paycheck"]) == pytest.approx(
        Decimal(body["effective_per_paycheck_total"])
        + Decimal(h["funding_account_drift"])
        + Decimal(h["forward_reminder_change"]),
        abs=Decimal("0.02"),
    )


@pytest.mark.django_db
@pytest.mark.api
def test_allocation_never_exceeds_capacity(api_client, planned_contribution):
    """The plan must fit the pot by construction, not by coincidence.

    Solving each bucket alone and summing could return any total at all; on real
    data it asked for 3,666 a paycheck against 2,820 scheduled and called the
    difference a shortfall.
    """
    body = api_client.get("/planning/planner/analysis", headers=AUTH).json()
    allocation = body["allocation"]

    capacity = Decimal(allocation["capacity_per_paycheck"])
    assert Decimal(allocation["allocated_total"]) <= capacity + Decimal("0.05")
    # And it is genuinely distributed, not just capped.
    granted = sum(
        Decimal(r["allocated_per_paycheck"])
        for r in body["rows"]
        if r["suggestion"]
    )
    assert granted == pytest.approx(
        Decimal(allocation["allocated_total"]), abs=Decimal("0.05")
    )


@pytest.mark.django_db
@pytest.mark.api
def test_apply_writes_the_allocated_amount_not_the_wish(
    api_client, planned_contribution, test_savings_account
):
    """What gets written is what the page showed.

    A contribution's share depends on every other one, so re-solving each row on
    its own during apply would write a figure that was never displayed.
    """
    from planning.models import Contribution

    Contribution.objects.create(
        contribution="College",
        per_paycheck=Decimal("5.00"),
        account=test_savings_account,
        goal_type=Contribution.GOAL_MAXIMISE,
    )
    body = api_client.get("/planning/planner/analysis", headers=AUTH).json()
    row = next(
        r
        for r in body["rows"]
        if r["contribution_id"] == planned_contribution.id
    )
    expected = Decimal(row["allocated_per_paycheck"])

    response = api_client.post(
        "/planning/planner/apply",
        json={"contribution_ids": [planned_contribution.id]},
        headers=AUTH,
    )

    assert response.status_code == 200
    result = response.json()["results"][0]
    assert result["applied"] is True
    assert Decimal(result["new_per_paycheck"]) == pytest.approx(
        expected, abs=Decimal("0.02")
    )
    planned_contribution.refresh_from_db()
    assert planned_contribution.per_paycheck == pytest.approx(
        expected, abs=Decimal("0.02")
    )
