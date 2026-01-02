import pytest
from planning.models import Note
from django.utils import timezone
import pytz
import os


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.mark.django_db
def test_note_creation():
    note = Note.objects.create(note_text="Test Note", note_date=current_date())

    assert note.id is not None
    assert note.note_text == "Test Note"
    assert note.note_date == current_date()


@pytest.mark.django_db
def test_note_defaults():
    note = Note.objects.create(note_text="Test Note")

    assert note.id is not None
    assert note.note_date == current_date()


@pytest.mark.django_db
def test_note_string_representation():
    note = Note.objects.create(note_text="Test Note")
    expected = str(current_date())

    assert str(note) == expected
