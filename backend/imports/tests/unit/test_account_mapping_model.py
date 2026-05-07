import pytest
from imports.models import AccountMapping


@pytest.mark.django_db
def test_account_mapping_creation(test_file_import):
    account_mapping = AccountMapping.objects.create(
        file_account="File Account", account_id=1, file_import=test_file_import
    )

    assert account_mapping.id is not None
    assert account_mapping.file_account == "File Account"
    assert account_mapping.account_id == 1
    assert account_mapping.file_import == test_file_import


@pytest.mark.django_db
def test_file_import_foreign_key_cascade_delete(test_file_import):
    AccountMapping.objects.create(
        file_account="File Account", account_id=1, file_import=test_file_import
    )

    assert AccountMapping.objects.count() == 1
    test_file_import.delete()
    assert AccountMapping.objects.count() == 0
