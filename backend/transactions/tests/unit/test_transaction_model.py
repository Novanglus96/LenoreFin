import pytest
from transactions.models import Transaction
from django.utils import timezone
import pytz
import os


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.mark.django_db
def test_transaction_creation(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
):
    transaction = Transaction.objects.create(
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
    )

    assert transaction.id is not None
    assert transaction.transaction_date == current_date()
    assert transaction.total_amount == 1.00
    assert transaction.status == test_pending_transaction_status
    assert transaction.memo == "Memo"
    assert transaction.description == "Description"
    assert transaction.edit_date == current_date()
    assert transaction.add_date == current_date()
    assert transaction.transaction_type == test_expense_transaction_type
    assert transaction.paycheck == test_paycheck
    assert transaction.checkNumber is None
    assert transaction.source_account == test_checking_account
    assert transaction.destination_account is None


@pytest.mark.django_db
def test_transaction_defaults(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
):
    transaction = Transaction.objects.create(
        status=test_pending_transaction_status,
        description="Description",
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
    )

    assert transaction.id is not None
    assert transaction.transaction_date == current_date()
    assert transaction.total_amount == 0.00
    assert transaction.memo is None
    assert transaction.edit_date == current_date()
    assert transaction.add_date == current_date()
    assert transaction.transaction_type == test_expense_transaction_type
    assert transaction.paycheck is None
    assert transaction.checkNumber is None
    assert transaction.source_account == test_checking_account
    assert transaction.destination_account is None


@pytest.mark.django_db
def test_transaction_string_representation(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
):
    transaction = Transaction.objects.create(
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
    )
    expected = f"{current_date()} : Description ($1.00)"

    assert transaction.id is not None
    assert str(transaction) == f"#{transaction.id} | {expected}"


@pytest.mark.django_db
def test_status_foreign_key_set_null_delete(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
):
    transaction = Transaction.objects.create(
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
    )
    assert transaction.id is not None
    assert transaction.status is not None
    test_pending_transaction_status.delete()
    transaction.refresh_from_db()
    assert transaction.status is None


@pytest.mark.django_db
def test_transaction_type_foreign_key_set_null_delete(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
):
    transaction = Transaction.objects.create(
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
    )
    assert transaction.id is not None
    assert transaction.transaction_type is not None
    test_expense_transaction_type.delete()
    transaction.refresh_from_db()
    assert transaction.transaction_type is None


@pytest.mark.django_db
def test_paycheck_foreign_key_set_null_delete(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
):
    transaction = Transaction.objects.create(
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
    )
    assert transaction.id is not None
    assert transaction.paycheck is not None
    test_paycheck.delete()
    transaction.refresh_from_db()
    assert transaction.paycheck is None


@pytest.mark.django_db
def test_source_account_foreign_key_cascade_delete(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
):
    transaction = Transaction.objects.create(
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
    )
    assert transaction.id is not None
    assert transaction.source_account is not None
    test_checking_account.delete()
    transaction.refresh_from_db()
    assert transaction.source_account is None


@pytest.mark.django_db
def test_destination_account_foreign_key_cascade_delete(
    test_paycheck,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
    test_savings_account,
):
    transaction = Transaction.objects.create(
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
    )
    assert transaction.id is not None
    assert transaction.destination_account is not None
    test_savings_account.delete()
    transaction.refresh_from_db()
    assert transaction.destination_account is None
