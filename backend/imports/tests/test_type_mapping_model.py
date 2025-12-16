import pytest
from imports.models import TypeMapping


@pytest.mark.django_db
def test_type_mapping_creation(test_file_import):
    type_mapping = TypeMapping.objects.create(
        file_type="File Type", type_id=1, file_import=test_file_import
    )

    assert type_mapping.id is not None
    assert type_mapping.file_type == "File Type"
    assert type_mapping.type_id == 1
    assert type_mapping.file_import == test_file_import


@pytest.mark.django_db
def test_file_import_foreign_key_cascade_delete(test_file_import):
    TypeMapping.objects.create(
        file_type="File Type", type_id=1, file_import=test_file_import
    )

    assert TypeMapping.objects.count() == 1
    test_file_import.delete()
    assert TypeMapping.objects.count() == 0
