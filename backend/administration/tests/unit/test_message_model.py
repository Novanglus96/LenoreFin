import pytest
from administration.models import Message
from django.utils import timezone
import pytz
import os


def current_date_time():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone)
    return today_tz


@pytest.mark.django_db
def test_message_creation():
    before = current_date_time()
    message = Message.objects.create(
        message_date=current_date_time(),
        message="This is a test message.",
        unread=True,
    )
    after = current_date_time()

    assert before <= message.message_date <= after
    assert message.message == "This is a test message."
    assert message.unread


@pytest.mark.django_db
def test_message_defaults():
    before = current_date_time()
    message = Message.objects.create(
        message="This is a test message.",
    )
    after = current_date_time()

    assert before <= message.message_date <= after
    assert message.unread


@pytest.mark.django_db
def test_message_string_representation():
    message = Message.objects.create(
        message_date=current_date_time(),
        message="This is a test message.",
        unread=True,
    )

    expected = "This is a test message."

    assert str(message) == expected
