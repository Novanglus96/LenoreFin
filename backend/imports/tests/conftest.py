import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from imports.models import FileImport, TransactionImport
from django.utils import timezone
import pytz
import os


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


@pytest.fixture
def test_file():
    return SimpleUploadedFile(
        "transactions.csv",
        b"id,amount,date\n1,100,2024-01-01\n",
        content_type="text/csv",
    )


@pytest.fixture
def test_file_import(test_file, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path

    return FileImport.objects.create(import_file=test_file)


@pytest.fixture
def test_transaction_import(test_file_import):
    return TransactionImport.objects.create(
        line_id=1,
        transaction_date=current_date(),
        transaction_type_id=1,
        transaction_status_id=1,
        description="Description",
        source_account_id=1,
        memo="Memo",
        file_import=test_file_import,
    )
