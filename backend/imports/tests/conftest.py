import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from imports.models import FileImport


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
