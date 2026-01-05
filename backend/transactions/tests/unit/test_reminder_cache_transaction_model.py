import pytest
from transactions.models import ReminderCacheTransaction
from django.utils import timezone
import pytz
import os


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.mark.django_db
def test_reminder_cache_transaction_creation(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
    test_reminder,
):
    reminder_cache_transaction = ReminderCacheTransaction.objects.create(
        transaction_date=current_date(),
        total_amount=1.00,
        status=test_pending_transaction_status,
        memo="Memo",
        description="Description",
        edit_date=current_date(),
        add_date=current_date(),
        transaction_type=test_expense_transaction_type,
        paycheck=test_paycheck,
        checkNumber=None,
        source_account=test_checking_account,
        destination_account=None,
        reminder=test_reminder,
    )

    assert reminder_cache_transaction.id is not None
    assert reminder_cache_transaction.transaction_date == current_date()
    assert reminder_cache_transaction.total_amount == 1.00
    assert reminder_cache_transaction.status == test_pending_transaction_status
    assert reminder_cache_transaction.memo == "Memo"
    assert reminder_cache_transaction.description == "Description"
    assert reminder_cache_transaction.edit_date == current_date()
    assert reminder_cache_transaction.add_date == current_date()
    assert (
        reminder_cache_transaction.transaction_type
        == test_expense_transaction_type
    )
    assert reminder_cache_transaction.paycheck == test_paycheck
    assert reminder_cache_transaction.checkNumber is None
    assert reminder_cache_transaction.source_account == test_checking_account
    assert reminder_cache_transaction.destination_account is None
    assert reminder_cache_transaction.reminder == test_reminder


@pytest.mark.django_db
def test_reminder_cache_transaction_defaults(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
    test_reminder,
):
    reminder_cache_transaction = ReminderCacheTransaction.objects.create(
        status=test_pending_transaction_status,
        description="Description",
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        reminder=test_reminder,
    )

    assert reminder_cache_transaction.id is not None
    assert reminder_cache_transaction.transaction_date == current_date()
    assert reminder_cache_transaction.total_amount == 0.00
    assert reminder_cache_transaction.memo is None
    assert reminder_cache_transaction.edit_date == current_date()
    assert reminder_cache_transaction.add_date == current_date()
    assert (
        reminder_cache_transaction.transaction_type
        == test_expense_transaction_type
    )
    assert reminder_cache_transaction.paycheck is None
    assert reminder_cache_transaction.checkNumber is None
    assert reminder_cache_transaction.source_account == test_checking_account
    assert reminder_cache_transaction.destination_account is None


@pytest.mark.django_db
def test_reminder_cache_transaction_string_representation(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
    test_reminder,
):
    reminder_cache_transaction = ReminderCacheTransaction.objects.create(
        transaction_date=current_date(),
        total_amount=1.00,
        status=test_pending_transaction_status,
        memo="Memo",
        description="Description",
        edit_date=current_date(),
        add_date=current_date(),
        transaction_type=test_expense_transaction_type,
        paycheck=test_paycheck,
        checkNumber=None,
        source_account=test_checking_account,
        destination_account=None,
        reminder=test_reminder,
    )
    expected = f"{current_date()} : Description ($1.00)"

    assert reminder_cache_transaction.id is not None
    assert (
        str(reminder_cache_transaction)
        == f"#{reminder_cache_transaction.id} | {expected}"
    )


@pytest.mark.django_db
def test_status_foreign_key_set_null_delete(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
    test_reminder,
):
    reminder_cache_transaction = ReminderCacheTransaction.objects.create(
        transaction_date=current_date(),
        total_amount=1.00,
        status=test_pending_transaction_status,
        memo="Memo",
        description="Description",
        edit_date=current_date(),
        add_date=current_date(),
        transaction_type=test_expense_transaction_type,
        paycheck=test_paycheck,
        checkNumber=None,
        source_account=test_checking_account,
        destination_account=None,
        reminder=test_reminder,
    )
    assert reminder_cache_transaction.id is not None
    assert reminder_cache_transaction.status is not None
    test_pending_transaction_status.delete()
    reminder_cache_transaction.refresh_from_db()
    assert reminder_cache_transaction.status is None


@pytest.mark.django_db
def test_reminder_cache_transaction_type_foreign_key_set_null_delete(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
    test_reminder,
):
    reminder_cache_transaction = ReminderCacheTransaction.objects.create(
        transaction_date=current_date(),
        total_amount=1.00,
        status=test_pending_transaction_status,
        memo="Memo",
        description="Description",
        edit_date=current_date(),
        add_date=current_date(),
        transaction_type=test_expense_transaction_type,
        paycheck=test_paycheck,
        checkNumber=None,
        source_account=test_checking_account,
        destination_account=None,
        reminder=test_reminder,
    )
    assert reminder_cache_transaction.id is not None
    assert reminder_cache_transaction.transaction_type is not None
    test_expense_transaction_type.delete()
    reminder_cache_transaction.refresh_from_db()
    assert reminder_cache_transaction.transaction_type is None


@pytest.mark.django_db
def test_paycheck_foreign_key_set_null_delete(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
    test_reminder,
):
    reminder_cache_transaction = ReminderCacheTransaction.objects.create(
        transaction_date=current_date(),
        total_amount=1.00,
        status=test_pending_transaction_status,
        memo="Memo",
        description="Description",
        edit_date=current_date(),
        add_date=current_date(),
        transaction_type=test_expense_transaction_type,
        paycheck=test_paycheck,
        checkNumber=None,
        source_account=test_checking_account,
        destination_account=None,
        reminder=test_reminder,
    )
    assert reminder_cache_transaction.id is not None
    assert reminder_cache_transaction.paycheck is not None
    test_paycheck.delete()
    reminder_cache_transaction.refresh_from_db()
    assert reminder_cache_transaction.paycheck is None


@pytest.mark.django_db
def test_source_account_foreign_key_cascade_delete(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
    test_reminder,
):
    reminder_cache_transaction = ReminderCacheTransaction.objects.create(
        transaction_date=current_date(),
        total_amount=1.00,
        status=test_pending_transaction_status,
        memo="Memo",
        description="Description",
        edit_date=current_date(),
        add_date=current_date(),
        transaction_type=test_expense_transaction_type,
        paycheck=test_paycheck,
        checkNumber=None,
        source_account=test_checking_account,
        destination_account=None,
        reminder=test_reminder,
    )
    assert reminder_cache_transaction.id is not None
    assert reminder_cache_transaction.source_account is not None
    test_checking_account.delete()
    reminder_cache_transaction.refresh_from_db()
    assert reminder_cache_transaction.source_account is None


@pytest.mark.django_db
def test_destination_account_foreign_key_cascade_delete(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
    test_savings_account,
    test_reminder,
):
    reminder_cache_transaction = ReminderCacheTransaction.objects.create(
        transaction_date=current_date(),
        total_amount=1.00,
        status=test_pending_transaction_status,
        memo="Memo",
        description="Description",
        edit_date=current_date(),
        add_date=current_date(),
        transaction_type=test_expense_transaction_type,
        paycheck=test_paycheck,
        checkNumber=None,
        source_account=test_checking_account,
        destination_account=test_savings_account,
        reminder=test_reminder,
    )
    assert reminder_cache_transaction.id is not None
    assert reminder_cache_transaction.destination_account is not None
    test_savings_account.delete()
    reminder_cache_transaction.refresh_from_db()
    assert reminder_cache_transaction.destination_account is None


@pytest.mark.django_db
def test_reminder_foreign_key_cascade_delete(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
    test_savings_account,
    test_reminder,
):
    ReminderCacheTransaction.objects.create(
        transaction_date=current_date(),
        total_amount=1.00,
        status=test_pending_transaction_status,
        memo="Memo",
        description="Description",
        edit_date=current_date(),
        add_date=current_date(),
        transaction_type=test_expense_transaction_type,
        paycheck=test_paycheck,
        checkNumber=None,
        source_account=test_checking_account,
        destination_account=test_savings_account,
        reminder=test_reminder,
    )
    assert ReminderCacheTransaction.objects.count() == 1
    test_reminder.delete()
    assert ReminderCacheTransaction.objects.count() == 0
