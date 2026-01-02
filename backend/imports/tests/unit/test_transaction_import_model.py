import pytest
from imports.models import TransactionImport
from django.utils import timezone
import pytz
import os


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.mark.django_db
def test_transaction_import_creation(test_file_import):
    transaction_import = TransactionImport.objects.create(
        line_id=1,
        transaction_date=current_date(),
        transaction_type_id=1,
        transaction_status_id=1,
        amount=0.00,
        description="Description",
        source_account_id=1,
        destination_account_id=None,
        memo="Memo",
        file_import=test_file_import,
    )

    assert transaction_import.id is not None
    assert transaction_import.line_id == 1
    assert transaction_import.transaction_date == current_date()
    assert transaction_import.transaction_type_id == 1
    assert transaction_import.transaction_status_id == 1
    assert transaction_import.amount == 0.00
    assert transaction_import.description == "Description"
    assert transaction_import.source_account_id == 1
    assert transaction_import.destination_account_id is None
    assert transaction_import.memo == "Memo"
    assert transaction_import.file_import == test_file_import


@pytest.mark.django_db
def test_transaction_import_defaults(test_file_import):
    transaction_import = TransactionImport.objects.create(
        line_id=1,
        transaction_date=current_date(),
        transaction_type_id=1,
        transaction_status_id=1,
        description="Description",
        source_account_id=1,
        memo="Memo",
        file_import=test_file_import,
    )

    assert transaction_import.amount == 0.00
    assert transaction_import.destination_account_id is None


@pytest.mark.django_db
def test_transaction_import_foreign_key_cascade_delete(test_file_import):
    TransactionImport.objects.create(
        line_id=1,
        transaction_date=current_date(),
        transaction_type_id=1,
        transaction_status_id=1,
        description="Description",
        source_account_id=1,
        memo="Memo",
        file_import=test_file_import,
    )

    assert TransactionImport.objects.count() == 1
    test_file_import.delete()
    assert TransactionImport.objects.count() == 0
