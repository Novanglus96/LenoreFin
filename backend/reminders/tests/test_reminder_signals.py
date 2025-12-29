import pytest
from unittest.mock import patch, call
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
@patch("reminders.signals.async_task")
def test_new_reminder_triggers_cache_update(
    mock_async_task,
    test_expense_transaction_type,
    test_checking_account,
    test_tag,
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

    mock_async_task.assert_called_once_with(
        "transactions.tasks.update_reminder_cache",
        reminder.id,
    )


@pytest.mark.django_db
@patch("reminders.signals.async_task")
def test_reminder_update_triggers_cache_update(
    mock_async_task,
    test_expense_transaction_type,
    test_checking_account,
    test_tag,
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
    mock_async_task.reset_mock()

    reminder.amount = 2.00
    reminder.save()

    mock_async_task.assert_called_once()


@pytest.mark.django_db
@patch("reminders.signals.delete_pattern")
def test_reminder_save_invalidates_source_account_cache(
    mock_delete_pattern,
    test_expense_transaction_type,
    test_checking_account,
    test_tag,
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

    expected_calls = [
        call(
            f"*account_{reminder.reminder_source_account.id}_reminder_transactions*"
        ),
        call(f"*account_{reminder.reminder_source_account.id}_transactions*"),
    ]

    mock_delete_pattern.assert_has_calls(
        expected_calls,
        any_order=True,
    )

    assert mock_delete_pattern.call_count == 2


@pytest.mark.django_db
@patch("reminders.signals.delete_pattern")
def test_reminder_save_invalidates_destination_account_cache(
    mock_delete_pattern,
    test_expense_transaction_type,
    test_checking_account,
    test_savings_account,
    test_tag,
):
    repeat = Repeat.objects.create(repeat_name="Test Repeat")
    reminder = Reminder.objects.create(
        tag=test_tag,
        amount=1.00,
        reminder_source_account=test_checking_account,
        reminder_destination_account=test_savings_account,
        description="Description",
        transaction_type=test_expense_transaction_type,
        start_date=current_date(),
        next_date=current_date(),
        end_date=current_date(),
        repeat=repeat,
        auto_add=True,
        memo="Memo",
    )

    expected_calls = [
        call(
            f"*account_{reminder.reminder_destination_account.id}_reminder_transactions*"
        ),
        call(
            f"*account_{reminder.reminder_destination_account.id}_transactions*"
        ),
    ]

    mock_delete_pattern.assert_has_calls(
        expected_calls,
        any_order=True,
    )

    assert mock_delete_pattern.call_count == 4


@pytest.mark.django_db
@patch("reminders.signals.delete_pattern")
def test_reminder_delete_invalidates_cache(
    mock_delete_pattern,
    test_expense_transaction_type,
    test_checking_account,
    test_savings_account,
    test_tag,
):
    repeat = Repeat.objects.create(repeat_name="Test Repeat")
    reminder = Reminder.objects.create(
        tag=test_tag,
        amount=1.00,
        reminder_source_account=test_checking_account,
        reminder_destination_account=test_savings_account,
        description="Description",
        transaction_type=test_expense_transaction_type,
        start_date=current_date(),
        next_date=current_date(),
        end_date=current_date(),
        repeat=repeat,
        auto_add=True,
        memo="Memo",
    )
    source_id = reminder.reminder_source_account.id
    reminder.delete()

    expected_calls = [
        call(f"*account_{source_id}_reminder_transactions*"),
        call(f"*account_{source_id}_transactions*"),
    ]

    mock_delete_pattern.assert_has_calls(
        expected_calls,
        any_order=True,
    )


@pytest.mark.django_db
@patch("reminders.signals.delete_pattern")
def test_reminder_save_invalidates_exactly_expected_patterns(
    mock_delete_pattern,
    test_expense_transaction_type,
    test_checking_account,
    test_savings_account,
    test_tag,
):
    repeat = Repeat.objects.create(repeat_name="Test Repeat")
    reminder = Reminder.objects.create(
        tag=test_tag,
        amount=1.00,
        reminder_source_account=test_checking_account,
        reminder_destination_account=test_savings_account,
        description="Description",
        transaction_type=test_expense_transaction_type,
        start_date=current_date(),
        next_date=current_date(),
        end_date=current_date(),
        repeat=repeat,
        auto_add=True,
        memo="Memo",
    )

    calls = {call.args[0] for call in mock_delete_pattern.call_args_list}

    expected = {
        f"*account_{reminder.reminder_source_account.id}_reminder_transactions*",
        f"*account_{reminder.reminder_destination_account.id}_reminder_transactions*",
        f"*account_{reminder.reminder_source_account.id}_transactions*",
        f"*account_{reminder.reminder_destination_account.id}_transactions*",
    }

    assert calls == expected
