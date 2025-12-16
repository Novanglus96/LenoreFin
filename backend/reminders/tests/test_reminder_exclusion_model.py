import pytest
from reminders.models import ReminderExclusion, Reminder, Repeat
from django.utils import timezone
import pytz
import os


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.mark.django_db
def test_reminder_exclusion_creation(
    test_expense_transaction_type, test_checking_account, test_tag
):
    repeat = Repeat.objects.create(repeat_name="Test Repeat")
    reminder = Reminder.objects.create(
        tag=test_tag,
        reminder_source_account=test_checking_account,
        reminder_destination_account=None,
        description="Description",
        transaction_type=test_expense_transaction_type,
        repeat=repeat,
    )
    reminder_exclusion = ReminderExclusion.objects.create(
        reminder=reminder, exclude_date=current_date()
    )

    assert reminder_exclusion.id is not None
    assert reminder_exclusion.reminder == reminder
    assert reminder_exclusion.exclude_date == current_date()


@pytest.mark.django_db
def test_reminder_exclusion_detaults(
    test_expense_transaction_type, test_checking_account, test_tag
):
    repeat = Repeat.objects.create(repeat_name="Test Repeat")
    reminder = Reminder.objects.create(
        tag=test_tag,
        reminder_source_account=test_checking_account,
        reminder_destination_account=None,
        description="Description",
        transaction_type=test_expense_transaction_type,
        repeat=repeat,
    )
    reminder_exclusion = ReminderExclusion.objects.create(reminder=reminder)

    assert reminder_exclusion.id is not None
    assert reminder_exclusion.exclude_date == current_date()


@pytest.mark.django_db
def test_reminder_foreign_key_cascade_delete(
    test_expense_transaction_type, test_checking_account, test_tag
):
    repeat = Repeat.objects.create(repeat_name="Test Repeat")
    reminder = Reminder.objects.create(
        tag=test_tag,
        reminder_source_account=test_checking_account,
        reminder_destination_account=None,
        description="Description",
        transaction_type=test_expense_transaction_type,
        repeat=repeat,
    )
    ReminderExclusion.objects.create(reminder=reminder)

    assert ReminderExclusion.objects.count() == 1
    reminder.delete()
    assert ReminderExclusion.objects.count() == 0
