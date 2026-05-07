import pytest
from django.utils import timezone
import pytz
import os


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    return today.astimezone(tz_timezone).date()


AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_create_reminder(api_client, test_reminder):
    response = api_client.post(
        "/reminders/create",
        json={
            "tag_id": test_reminder.tag.id,
            "amount": "50.00",
            "reminder_source_account_id": test_reminder.reminder_source_account.id,
            "reminder_destination_account_id": None,
            "description": "API Test Reminder",
            "transaction_type_id": test_reminder.transaction_type.id,
            "start_date": current_date().isoformat(),
            "next_date": None,
            "end_date": None,
            "repeat_id": test_reminder.repeat.id,
            "auto_add": False,
            "memo": None,
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.django_db
@pytest.mark.api
def test_get_reminder(api_client, test_reminder):
    response = api_client.get(
        f"/reminders/get/{test_reminder.id}", headers=AUTH
    )

    assert response.status_code == 200
    assert response.json()["id"] == test_reminder.id
    assert response.json()["description"] == test_reminder.description


@pytest.mark.django_db
@pytest.mark.api
def test_list_reminders(api_client, test_reminder):
    response = api_client.get("/reminders/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.django_db
@pytest.mark.api
def test_update_reminder(api_client, test_reminder):
    response = api_client.put(
        f"/reminders/update/{test_reminder.id}",
        json={
            "tag_id": test_reminder.tag.id,
            "amount": "75.00",
            "reminder_source_account_id": test_reminder.reminder_source_account.id,
            "reminder_destination_account_id": None,
            "description": "Updated Reminder",
            "transaction_type_id": test_reminder.transaction_type.id,
            "start_date": current_date().isoformat(),
            "next_date": None,
            "end_date": None,
            "repeat_id": test_reminder.repeat.id,
            "auto_add": False,
            "memo": None,
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    test_reminder.refresh_from_db()
    assert test_reminder.description == "Updated Reminder"


@pytest.mark.django_db
@pytest.mark.api
def test_delete_reminder(api_client, test_reminder):
    response = api_client.delete(
        f"/reminders/delete/{test_reminder.id}", headers=AUTH
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    from reminders.models import Reminder
    assert not Reminder.objects.filter(id=test_reminder.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_get_reminder_not_found(api_client):
    response = api_client.get("/reminders/get/9999", headers=AUTH)

    assert response.status_code == 404
