"""Rebuilding a reminder's forecast cache replaces its rows, never adds to them.

Accepting a savings plan rebuilds the reminders it writes inline, while the
save signal queues the same rebuild on the worker. Before the rebuild ran under
a row lock, overlapping runs left both sets of rows behind and every transfer
showed twice in the forecast.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest

from reminders.models import Reminder, Repeat
from transactions.models import ReminderCacheTransaction, TransactionStatus
from transactions.tasks import update_reminder_cache


@pytest.mark.django_db
@pytest.mark.service
def test_rebuilding_twice_leaves_one_row_per_occurrence(
    test_tag,
    test_checking_account,
    test_savings_account,
    test_transfer_transaction_type,
    test_income_transaction_type,
    test_expense_transaction_type,
):
    TransactionStatus.objects.create(transaction_status="Pending")
    biweekly = Repeat.objects.create(repeat_name="Every 2 Weeks (cache test)", weeks=2)
    today = date(2026, 11, 23)
    with patch("transactions.tasks.get_todays_date_timezone_adjusted", return_value=today), \
         patch("reminders.signals.async_task"):
        reminder = Reminder.objects.create(
            tag=test_tag,
            amount=Decimal("-1645.00"),
            reminder_source_account=test_checking_account,
            reminder_destination_account=test_savings_account,
            description="Transfer to House",
            transaction_type=test_transfer_transaction_type,
            repeat=biweekly,
            start_date=date(2027, 1, 2),
            next_date=date(2027, 1, 2),
            end_date=date(2027, 3, 1),
        )
        update_reminder_cache(reminder.pk)
        update_reminder_cache(reminder.pk)

    dates = list(
        ReminderCacheTransaction.objects.filter(reminder=reminder)
        .order_by("transaction_date")
        .values_list("transaction_date", flat=True)
    )
    assert dates == [
        date(2027, 1, 2), date(2027, 1, 16), date(2027, 1, 30),
        date(2027, 2, 13), date(2027, 2, 27),
    ]
