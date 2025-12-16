import pytest
from reminders.models import Reminder, Repeat
from django.utils import timezone
import pytz
import os


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.mark.django_db
def test_reminder_creation(
    test_expense_transaction_type, test_checking_account, test_tag
):
    repeat = Repeat.objects.create(repeat_name="Test Repeat")
    reminder = Reminder.objects.create(
        tag=test_tag,
        amount=1.00,
        reminder_source_account=test_checking_account,
        reminder_destination_account=None,
        description="Description",
        transaction_type=test_expense_transaction_type,
        start_date=current_date(),
        next_date=current_date(),
        end_date=current_date(),
        repeat=repeat,
        auto_add=True,
        memo="Memo",
    )

    assert reminder.id is not None
    assert reminder.tag == test_tag
    assert reminder.amount == 1.00
    assert reminder.reminder_source_account == test_checking_account
    assert reminder.reminder_destination_account is None
    assert reminder.description == "Description"
    assert reminder.transaction_type == test_expense_transaction_type
    assert reminder.start_date == current_date()
    assert reminder.next_date == current_date()
    assert reminder.end_date == current_date()
    assert reminder.repeat == repeat
    assert reminder.auto_add
    assert reminder.memo == "Memo"


@pytest.mark.django_db
def test_reminder_defaults(
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

    assert reminder.id is not None
    assert reminder.amount == 0.00
    assert reminder.start_date == current_date()
    assert reminder.next_date is None
    assert reminder.end_date is None
    assert not reminder.auto_add
    assert reminder.memo is None


@pytest.mark.django_db
def test_reminder_string_representation(
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
    expected = "Description"

    assert str(reminder) == expected


@pytest.mark.django_db
def test_tag_foreign_key_setnull_delete(
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

    assert reminder.id is not None
    assert reminder.tag is not None
    test_tag.delete()
    reminder.refresh_from_db()
    assert reminder.tag is None


@pytest.mark.django_db
def test_reminder_source_account_foreign_key_setnull_delete(
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

    assert reminder.id is not None
    assert reminder.reminder_source_account is not None
    test_checking_account.delete()
    reminder.refresh_from_db()
    assert reminder.reminder_source_account is None


@pytest.mark.django_db
def test_reminder_destination_account_foreign_key_setnull_delete(
    test_expense_transaction_type,
    test_checking_account,
    test_tag,
    test_savings_account,
):
    repeat = Repeat.objects.create(repeat_name="Test Repeat")
    reminder = Reminder.objects.create(
        tag=test_tag,
        reminder_source_account=test_savings_account,
        reminder_destination_account=test_checking_account,
        description="Description",
        transaction_type=test_expense_transaction_type,
        repeat=repeat,
    )

    assert reminder.id is not None
    assert reminder.reminder_destination_account is not None
    test_checking_account.delete()
    reminder.refresh_from_db()
    assert reminder.reminder_destination_account is None


@pytest.mark.django_db
def test_transaction_type_foreign_key_setnull_delete(
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

    assert reminder.id is not None
    assert reminder.transaction_type is not None
    test_expense_transaction_type.delete()
    reminder.refresh_from_db()
    assert reminder.transaction_type is None


@pytest.mark.django_db
def test_repeat_foreign_key_setnull_delete(
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

    assert reminder.id is not None
    assert reminder.repeat is not None
    repeat.delete()
    reminder.refresh_from_db()
    assert reminder.repeat is None
