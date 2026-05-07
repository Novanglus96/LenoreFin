import pytest
from imports.models import TransactionImportError


@pytest.mark.django_db
def test_transaction_import_error_creation(test_transaction_import):
    transaction_import_error = TransactionImportError.objects.create(
        text="Error Text", status=1, transaction_import=test_transaction_import
    )

    assert transaction_import_error.id is not None
    assert transaction_import_error.text == "Error Text"
    assert transaction_import_error.status == 1
    assert (
        transaction_import_error.transaction_import == test_transaction_import
    )


@pytest.mark.django_db
def test_transaction_import_foreign_key_cascade_delete(test_transaction_import):
    TransactionImportError.objects.create(
        text="Error Text", status=1, transaction_import=test_transaction_import
    )

    assert TransactionImportError.objects.count() == 1
    test_transaction_import.delete()
    assert TransactionImportError.objects.count() == 0
