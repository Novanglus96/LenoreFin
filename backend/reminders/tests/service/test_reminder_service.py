import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import patch, MagicMock
from transactions.models import Transaction
from reminders.models import ReminderExclusion
from reminders.services.reminder import add_reminder_transaction, ReminderNotFound


@pytest.mark.django_db
@pytest.mark.service
def test_add_reminder_transaction_creates_transaction(
    test_reminder,
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_checking_account,
    test_tag,
):
    """Calling add_reminder_transaction creates a Transaction record in the database."""
    transaction_date = date(2026, 3, 1)
    before_count = Transaction.objects.count()

    # The service hardcodes status_id=1 when building the FullTransaction.
    # Patch create_transactions to create the transaction directly so we control the status FK.
    def fake_create_transactions(transactions, *args, **kwargs):
        for t in transactions:
            Transaction.objects.create(
                transaction_date=t.transaction_date,
                total_amount=t.total_amount,
                status=test_pending_transaction_status,
                memo=t.memo,
                description=t.description,
                transaction_type_id=t.transaction_type_id,
                source_account_id=t.source_account_id,
                destination_account_id=t.destination_account_id,
                edit_date=t.edit_date,
                add_date=t.add_date,
            )

    with patch(
        "reminders.services.reminder.create_transactions",
        side_effect=fake_create_transactions,
    ):
        add_reminder_transaction(test_reminder.id, transaction_date)

    assert Transaction.objects.count() == before_count + 1
    created = Transaction.objects.latest("id")
    assert created.description == test_reminder.description
    assert created.transaction_date == transaction_date
    assert created.total_amount == Decimal(str(test_reminder.amount))


@pytest.mark.django_db
@pytest.mark.service
def test_add_reminder_transaction_creates_exclusion(
    test_reminder,
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_checking_account,
    test_tag,
):
    """Calling add_reminder_transaction creates a ReminderExclusion for the given date."""
    transaction_date = date(2026, 3, 2)

    with patch("reminders.services.reminder.create_transactions"):
        add_reminder_transaction(test_reminder.id, transaction_date)

    assert ReminderExclusion.objects.filter(
        reminder=test_reminder,
        exclude_date=transaction_date,
    ).exists()


@pytest.mark.django_db
@pytest.mark.service
def test_add_reminder_transaction_raises_for_nonexistent_reminder():
    """ReminderNotFound is raised when the given reminder_id does not exist."""
    with pytest.raises(ReminderNotFound):
        add_reminder_transaction(999999, date(2026, 3, 1))


@pytest.mark.django_db
@pytest.mark.service
def test_add_reminder_transaction_advances_start_date(
    test_reminder,
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_checking_account,
    test_tag,
):
    """Converting the current next_date advances start_date to the next non-excluded occurrence."""
    next_occurrence = date(2026, 4, 1)
    test_reminder.next_date = next_occurrence
    test_reminder.start_date = next_occurrence
    test_reminder.save()

    with patch("reminders.services.reminder.create_transactions"):
        add_reminder_transaction(test_reminder.id, next_occurrence)

    test_reminder.refresh_from_db()
    assert test_reminder.start_date != next_occurrence, (
        "start_date should advance past the converted date"
    )
    assert test_reminder.start_date == test_reminder.next_date


@pytest.mark.django_db
@pytest.mark.service
def test_add_reminder_transaction_advances_start_date_past_exclusions(
    test_reminder,
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_checking_account,
    test_tag,
):
    """start_date skips over any existing exclusions when advancing."""
    from reminders.models import ReminderExclusion

    base_date = date(2026, 5, 1)
    test_reminder.next_date = base_date
    test_reminder.start_date = base_date
    test_reminder.save()

    # Pre-exclude the two dates immediately after base_date so the loop must skip them
    repeat = test_reminder.repeat
    from dateutil.relativedelta import relativedelta
    skip1 = base_date + relativedelta(
        days=repeat.days, weeks=repeat.weeks, months=repeat.months, years=repeat.years
    )
    skip2 = skip1 + relativedelta(
        days=repeat.days, weeks=repeat.weeks, months=repeat.months, years=repeat.years
    )
    ReminderExclusion.objects.create(reminder=test_reminder, exclude_date=skip1)
    ReminderExclusion.objects.create(reminder=test_reminder, exclude_date=skip2)

    with patch("reminders.services.reminder.create_transactions"):
        add_reminder_transaction(test_reminder.id, base_date)

    test_reminder.refresh_from_db()
    assert test_reminder.start_date not in (base_date, skip1, skip2)
    assert test_reminder.start_date == test_reminder.next_date


@pytest.mark.django_db
@pytest.mark.service
def test_add_reminder_transaction_skips_duplicate_transaction(
    test_reminder,
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_checking_account,
    test_tag,
):
    """When a matching transaction already exists for the date, no new transaction is created."""
    transaction_date = date(2026, 3, 3)

    # Pre-create a transaction that matches the dedup query in the service
    Transaction.objects.create(
        transaction_date=transaction_date,
        total_amount=test_reminder.amount,
        memo=test_reminder.memo,
        description=test_reminder.description,
        transaction_type=test_reminder.transaction_type,
        destination_account=test_reminder.reminder_destination_account,
        source_account=test_reminder.reminder_source_account,
        status=test_pending_transaction_status,
    )

    before_count = Transaction.objects.count()

    mock_create = MagicMock()
    with patch("reminders.services.reminder.create_transactions", mock_create):
        add_reminder_transaction(test_reminder.id, transaction_date)

    # create_transactions should NOT have been called because the transaction already exists
    mock_create.assert_not_called()
    assert Transaction.objects.count() == before_count
