import pytest
from imports.models import TagMapping


@pytest.mark.django_db
def test_tag_mapping_creation(test_file_import):
    tag_mapping = TagMapping.objects.create(
        file_tag="File Tag", tag_id=1, file_import=test_file_import
    )

    assert tag_mapping.id is not None
    assert tag_mapping.file_tag == "File Tag"
    assert tag_mapping.tag_id == 1
    assert tag_mapping.file_import == test_file_import


@pytest.mark.django_db
def test_file_import_foreign_key_cascade_delete(test_file_import):
    TagMapping.objects.create(
        file_tag="File Tag", tag_id=1, file_import=test_file_import
    )

    assert TagMapping.objects.count() == 1
    test_file_import.delete()
    assert TagMapping.objects.count() == 0
