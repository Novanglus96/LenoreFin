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


@pytest.mark.django_db
def test_message_user_fk():
    from django.contrib.auth.models import User

    user = User.objects.create_user(username="msguser", password="pass")
    message = Message.objects.create(
        message="User-scoped message.",
        user=user,
    )

    assert message.user == user
    assert message.user_id == user.pk


@pytest.mark.django_db
def test_message_user_null_by_default():
    message = Message.objects.create(message="Global message.")

    assert message.user is None


@pytest.mark.django_db
def test_message_link_field():
    message = Message.objects.create(
        message="Link message.",
        link="/planning/detections",
    )

    assert message.link == "/planning/detections"


@pytest.mark.django_db
def test_message_link_null_by_default():
    message = Message.objects.create(message="No link.")

    assert message.link is None


@pytest.mark.django_db
def test_message_user_cascade_delete():
    from django.contrib.auth.models import User

    user = User.objects.create_user(username="cascadeuser", password="pass")
    message = Message.objects.create(message="Will be deleted.", user=user)
    message_id = message.id

    user.delete()

    assert not Message.objects.filter(id=message_id).exists()
