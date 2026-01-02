import pytest
from imports.models import TransactionImportTag


@pytest.mark.django_db
def test_transaction_import_tag_creation(test_transaction_import):
    transaction_import_tag = TransactionImportTag.objects.create(
        tag_id=1,
        tag_name="Test Tag",
        tag_amount=0.00,
        transaction_import=test_transaction_import,
    )

    assert transaction_import_tag.id is not None
    assert transaction_import_tag.tag_id == 1
    assert transaction_import_tag.tag_amount == 0.00
    assert transaction_import_tag.transaction_import == test_transaction_import


@pytest.mark.django_db
def test_transaction_import_tag_defaults(test_transaction_import):
    transaction_import_tag = TransactionImportTag.objects.create(
        tag_id=1,
        tag_name="Test Tag",
        transaction_import=test_transaction_import,
    )

    assert transaction_import_tag.tag_amount == 0.00


@pytest.mark.django_db
def test_transaction_import_foreign_key_cascade_delete(test_transaction_import):
    TransactionImportTag.objects.create(
        tag_id=1,
        tag_name="Test Tag",
        tag_amount=0.00,
        transaction_import=test_transaction_import,
    )

    assert TransactionImportTag.objects.count() == 1
    test_transaction_import.delete()
    assert TransactionImportTag.objects.count() == 0
