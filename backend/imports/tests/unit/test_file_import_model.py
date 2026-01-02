import pytest
from imports.models import FileImport
from django.core.files.uploadedfile import SimpleUploadedFile
import re


@pytest.mark.django_db
def test_file_import_upload(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path

    file = SimpleUploadedFile(
        "transactions.csv",
        b"id,amount,date\n1,100,2024-01-01\n",
        content_type="text/csv",
    )

    obj = FileImport.objects.create(import_file=file)

    assert obj.id is not None
    assert obj.import_file.name.startswith("imports/import-")
    assert obj.import_file.name.endswith(".csv")

    # Ensure file exists on disk
    assert (tmp_path / obj.import_file.name).exists()
    assert re.match(
        r"imports/import-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.csv",
        obj.import_file.name,
    )


@pytest.mark.django_db
def test_file_deleted_on_model_delete(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path

    file = SimpleUploadedFile(
        "transactions.csv",
        b"test data",
        content_type="text/csv",
    )

    obj = FileImport.objects.create(import_file=file)

    file_path = tmp_path / obj.import_file.name
    assert file_path.exists()

    obj.delete()

    assert not file_path.exists()


@pytest.mark.django_db
def test_file_import_defaults(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path

    file = SimpleUploadedFile(
        "transactions.csv",
        b"test data",
        content_type="text/csv",
    )

    obj = FileImport.objects.create(import_file=file)

    assert not obj.processed
    assert obj.successful is None
    assert obj.errors == 0
