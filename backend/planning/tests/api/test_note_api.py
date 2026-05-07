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
def test_note():
    from planning.models import Note

    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return Note.objects.create(note_text="Test note text", note_date=today_tz)


@pytest.mark.django_db
@pytest.mark.api
def test_create_note(api_client):
    response = api_client.post(
        "/planning/notes/create",
        json={
            "note_text": "A brand new note",
            "note_date": _today(),
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.django_db
@pytest.mark.api
def test_get_note(api_client, test_note):
    response = api_client.get(
        f"/planning/notes/get/{test_note.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_note.id
    assert data["note_text"] == test_note.note_text


@pytest.mark.django_db
@pytest.mark.api
def test_get_note_not_found(api_client):
    response = api_client.get("/planning/notes/get/9999", headers=AUTH)

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_update_note(api_client, test_note):
    response = api_client.put(
        f"/planning/notes/update/{test_note.id}",
        json={
            "note_text": "Updated note text",
            "note_date": _today(),
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.django_db
@pytest.mark.api
def test_update_note_not_found(api_client):
    response = api_client.put(
        "/planning/notes/update/9999",
        json={
            "note_text": "Ghost note",
            "note_date": _today(),
        },
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_list_notes(api_client, test_note):
    response = api_client.get("/planning/notes/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.django_db
@pytest.mark.api
def test_list_notes_ordered_descending(api_client):
    from planning.models import Note
    from datetime import date

    Note.objects.create(note_text="Older note", note_date=date(2023, 1, 1))
    Note.objects.create(note_text="Newer note", note_date=date(2024, 6, 15))

    response = api_client.get("/planning/notes/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    dates = [item["note_date"] for item in data]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
@pytest.mark.api
def test_delete_note(api_client, test_note):
    response = api_client.delete(
        f"/planning/notes/delete/{test_note.id}", headers=AUTH
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    from planning.models import Note

    assert not Note.objects.filter(id=test_note.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_delete_note_not_found(api_client):
    response = api_client.delete("/planning/notes/delete/9999", headers=AUTH)

    assert response.status_code == 404
