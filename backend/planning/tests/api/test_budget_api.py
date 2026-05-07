import pytest
from django.utils import timezone
import pytz
import os

AUTH = {"Authorization": "Bearer test-api-key"}


def _today():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz.isoformat()


@pytest.fixture
def test_repeat():
    from reminders.models import Repeat
    return Repeat.objects.create(
        repeat_name="Monthly", days=0, weeks=0, months=1, years=0
    )


@pytest.fixture
def test_budget(test_repeat):
    from planning.models import Budget

    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return Budget.objects.create(
        tag_ids="[]",
        name="Test Budget",
        amount=500.00,
        roll_over=False,
        repeat=test_repeat,
        start_day=today_tz,
        roll_over_amt=0.00,
        active=True,
        widget=False,
        next_start=today_tz,
    )


@pytest.mark.django_db
@pytest.mark.api
def test_create_budget(api_client, test_repeat):
    today = _today()
    response = api_client.post(
        "/planning/budget/create",
        json={
            "tag_ids": "[]",
            "name": "New Budget",
            "amount": "200.00",
            "roll_over": False,
            "repeat_id": test_repeat.id,
            "start_day": today,
            "roll_over_amt": "0.00",
            "active": True,
            "widget": False,
            "next_start": today,
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.django_db
@pytest.mark.api
def test_get_budget(api_client, test_budget):
    response = api_client.get(
        f"/planning/budget/get/{test_budget.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_budget.id
    assert data["name"] == test_budget.name


@pytest.mark.django_db
@pytest.mark.api
def test_get_budget_not_found(api_client):
    response = api_client.get("/planning/budget/get/9999", headers=AUTH)

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_update_budget(api_client, test_budget, test_repeat):
    today = _today()
    response = api_client.put(
        f"/planning/budget/update/{test_budget.id}",
        json={
            "tag_ids": "[]",
            "name": "Updated Budget",
            "amount": "600.00",
            "roll_over": False,
            "repeat_id": test_repeat.id,
            "start_day": today,
            "roll_over_amt": "0.00",
            "active": True,
            "widget": False,
            "next_start": today,
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.django_db
@pytest.mark.api
def test_update_budget_not_found(api_client, test_repeat):
    today = _today()
    response = api_client.put(
        "/planning/budget/update/9999",
        json={
            "tag_ids": "[]",
            "name": "Ghost Budget",
            "amount": "100.00",
            "roll_over": False,
            "repeat_id": test_repeat.id,
            "start_day": today,
            "roll_over_amt": "0.00",
            "active": True,
            "widget": False,
            "next_start": today,
        },
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_list_budgets(api_client, test_budget):
    response = api_client.get("/planning/budget/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.django_db
@pytest.mark.api
def test_delete_budget(api_client, test_budget):
    response = api_client.delete(
        f"/planning/budget/delete/{test_budget.id}", headers=AUTH
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    from planning.models import Budget

    assert not Budget.objects.filter(id=test_budget.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_delete_budget_not_found(api_client):
    response = api_client.delete("/planning/budget/delete/9999", headers=AUTH)

    assert response.status_code == 404
