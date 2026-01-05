import pytest
from reminders.models import Repeat
from django.utils import timezone
import pytz
import os
from django.db import IntegrityError


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.mark.django_db
def test_repeat_creation():
    repeat = Repeat.objects.create(
        repeat_name="Test Repeat", days=1, weeks=1, months=1, years=1
    )

    assert repeat.id is not None
    assert repeat.repeat_name == "Test Repeat"
    assert repeat.days == 1
    assert repeat.weeks == 1
    assert repeat.months == 1
    assert repeat.years == 1


@pytest.mark.django_db
def test_repeat_detaults():
    repeat = Repeat.objects.create(repeat_name="Test Repeat")

    assert repeat.id is not None
    assert repeat.days == 0
    assert repeat.weeks == 0
    assert repeat.months == 0
    assert repeat.years == 0


@pytest.mark.django_db
def test_repeat_name_uniqueness():
    Repeat.objects.create(repeat_name="Test Repeat")

    with pytest.raises(IntegrityError):
        Repeat.objects.create(repeat_name="Test Repeat")


@pytest.mark.django_db
def test_repeat_string_representation():
    repeat = Repeat.objects.create(repeat_name="Test Repeat")
    expected = "Test Repeat"

    assert str(repeat) == expected
