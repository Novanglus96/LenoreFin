import pytest
from datetime import date
from planning.models import DetectedRecurring
from reminders.models import Repeat


AUTH = {"Authorization": "Bearer test-api-key"}
LIST_URL = "/planning/detected-recurring/"
ITEM_BASE = "/planning/detected-recurring"


@pytest.fixture
def repeat(db):
    return Repeat.objects.create(repeat_name="Monthly", days=0, weeks=0, months=1, years=0)


def make_detection(description="Netflix", amount="15.99", repeat=None, ignored=False):
    return DetectedRecurring.objects.create(
        description=description,
        estimated_amount=amount,
        repeat=repeat,
        next_estimated_date=date(2026, 6, 15),
        transaction_ids=[1, 2, 3],
        is_ignored=ignored,
        suggested_tag_id=10,
        suggested_account_id=5,
    )


@pytest.mark.django_db
@pytest.mark.api
def test_list_detected_empty(api_client):
    response = api_client.get(LIST_URL, headers=AUTH)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
@pytest.mark.api
def test_list_detected_returns_active_only(api_client):
    make_detection("Active")
    make_detection("Ignored", ignored=True)

    response = api_client.get(LIST_URL, headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["description"] == "Active"


@pytest.mark.django_db
@pytest.mark.api
def test_list_detected_includes_suggested_fields(api_client):
    make_detection("Spotify")

    response = api_client.get(LIST_URL, headers=AUTH)

    assert response.status_code == 200
    item = response.json()[0]
    assert item["suggested_tag_id"] == 10
    assert item["suggested_account_id"] == 5


@pytest.mark.django_db
@pytest.mark.api
def test_list_detected_with_repeat(api_client, repeat):
    make_detection("Amazon Prime", repeat=repeat)

    response = api_client.get(LIST_URL, headers=AUTH)

    assert response.status_code == 200
    item = response.json()[0]
    assert item["repeat_id"] == repeat.id
    assert item["repeat_name"] == "Monthly"


@pytest.mark.django_db
@pytest.mark.api
def test_ignore_detection(api_client):
    detection = make_detection("CloudFlare")

    response = api_client.post(f"{ITEM_BASE}/{detection.id}/ignore", headers=AUTH)

    assert response.status_code == 200
    assert response.json()["success"] is True
    detection.refresh_from_db()
    assert detection.is_ignored is True


@pytest.mark.django_db
@pytest.mark.api
def test_ignore_detection_not_found(api_client):
    response = api_client.post(f"{ITEM_BASE}/99999/ignore", headers=AUTH)

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_ignore_detection_disappears_from_list(api_client):
    detection = make_detection("Hulu")
    api_client.post(f"{ITEM_BASE}/{detection.id}/ignore", headers=AUTH)

    response = api_client.get(LIST_URL, headers=AUTH)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
@pytest.mark.api
def test_delete_detection(api_client):
    detection = make_detection("Disney+")

    response = api_client.delete(f"{ITEM_BASE}/{detection.id}", headers=AUTH)

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert not DetectedRecurring.objects.filter(id=detection.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_delete_detection_not_found(api_client):
    response = api_client.delete(f"{ITEM_BASE}/99999", headers=AUTH)

    assert response.status_code == 404
