import pytest
from imports.models import StatusMapping


@pytest.mark.django_db
def test_status_mapping_creation(test_file_import):
    status_mapping = StatusMapping.objects.create(
        file_status="File Status", status_id=1, file_import=test_file_import
    )

    assert status_mapping.id is not None
    assert status_mapping.file_status == "File Status"
    assert status_mapping.status_id == 1
    assert status_mapping.file_import == test_file_import


@pytest.mark.django_db
def test_file_import_foreign_key_cascade_delete(test_file_import):
    StatusMapping.objects.create(
        file_status="File Status", status_id=1, file_import=test_file_import
    )

    assert StatusMapping.objects.count() == 1
    test_file_import.delete()
    assert StatusMapping.objects.count() == 0
