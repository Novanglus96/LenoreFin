import pytest
from datetime import date
from planning.models import DetectedRecurring
from reminders.models import Repeat


@pytest.fixture
def repeat():
    return Repeat.objects.create(repeat_name="Monthly", days=0, weeks=0, months=1, years=0)


@pytest.mark.django_db
def test_detected_recurring_creation(repeat):
    detection = DetectedRecurring.objects.create(
        description="Netflix",
        estimated_amount="15.99",
        repeat=repeat,
        next_estimated_date=date(2026, 6, 15),
        transaction_ids=[1, 2, 3],
    )

    assert detection.description == "Netflix"
    assert detection.estimated_amount == 15.99 or str(detection.estimated_amount) == "15.99"
    assert detection.repeat == repeat
    assert detection.next_estimated_date == date(2026, 6, 15)
    assert detection.transaction_ids == [1, 2, 3]
    assert detection.is_ignored is False
    assert detection.created_at is not None


@pytest.mark.django_db
def test_detected_recurring_string_representation(repeat):
    detection = DetectedRecurring.objects.create(
        description="Spotify",
        estimated_amount="9.99",
        repeat=repeat,
        next_estimated_date=date(2026, 6, 1),
        transaction_ids=[],
    )

    assert str(detection) == "Spotify"


@pytest.mark.django_db
def test_detected_recurring_is_ignored_default():
    detection = DetectedRecurring.objects.create(
        description="Amazon Prime",
        estimated_amount="14.99",
        next_estimated_date=date(2026, 7, 1),
        transaction_ids=[],
    )

    assert detection.is_ignored is False


@pytest.mark.django_db
def test_detected_recurring_no_repeat():
    detection = DetectedRecurring.objects.create(
        description="One-time",
        estimated_amount="50.00",
        next_estimated_date=date(2026, 8, 1),
        transaction_ids=[10],
    )

    assert detection.repeat is None


@pytest.mark.django_db
def test_detected_recurring_suggested_fields():
    detection = DetectedRecurring.objects.create(
        description="CloudFlare",
        estimated_amount="20.00",
        next_estimated_date=date(2026, 6, 1),
        transaction_ids=[5, 6],
        suggested_tag_id=42,
        suggested_account_id=7,
    )

    assert detection.suggested_tag_id == 42
    assert detection.suggested_account_id == 7


@pytest.mark.django_db
def test_detected_recurring_suggested_fields_null_by_default():
    detection = DetectedRecurring.objects.create(
        description="No suggestions",
        estimated_amount="10.00",
        next_estimated_date=date(2026, 6, 1),
        transaction_ids=[],
    )

    assert detection.suggested_tag_id is None
    assert detection.suggested_account_id is None


@pytest.mark.django_db
def test_detected_recurring_ordering_newest_first(repeat):
    d1 = DetectedRecurring.objects.create(
        description="First",
        estimated_amount="10.00",
        repeat=repeat,
        next_estimated_date=date(2026, 6, 1),
        transaction_ids=[],
    )
    d2 = DetectedRecurring.objects.create(
        description="Second",
        estimated_amount="20.00",
        repeat=repeat,
        next_estimated_date=date(2026, 7, 1),
        transaction_ids=[],
    )

    detections = list(DetectedRecurring.objects.all())
    assert detections[0].id == d2.id
    assert detections[1].id == d1.id
