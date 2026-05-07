import pytest
from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile
from imports.models import FileImport
from imports.services.import_file import process_file_import
from imports.api.schemas.import_file import (
    MappingDefinition,
    TypeMappingSchema,
    StatusMappingSchema,
    AccountMappingSchema,
    TagMappingSchema,
    TransactionImportSchema,
)


@pytest.fixture
def csv_file():
    return SimpleUploadedFile(
        "transactions.csv",
        b"id,amount,date\n1,100,2024-01-01\n",
        content_type="text/csv",
    )


@pytest.fixture
def minimal_payload(
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
    test_tag,
):
    return MappingDefinition(
        transaction_types=[
            TypeMappingSchema(
                file_type="Expense",
                type_id=test_expense_transaction_type.id,
            )
        ],
        transaction_statuses=[
            StatusMappingSchema(
                file_status="Pending",
                status_id=test_pending_transaction_status.id,
            )
        ],
        accounts=[
            AccountMappingSchema(
                file_account="Checking",
                account_id=test_checking_account.id,
            )
        ],
        tags=[
            TagMappingSchema(
                file_tag="Groceries",
                tag_id=test_tag.id,
            )
        ],
        transactions=[],
    )


@pytest.mark.django_db
@pytest.mark.service
def test_process_file_import_creates_file_import_record(
    csv_file,
    minimal_payload,
    tmp_path,
    settings,
):
    """process_file_import persists a FileImport record to the database."""
    settings.MEDIA_ROOT = tmp_path

    before_count = FileImport.objects.count()
    process_file_import(csv_file, minimal_payload)

    assert FileImport.objects.count() == before_count + 1


@pytest.mark.django_db
@pytest.mark.service
def test_process_file_import_returns_file_import_id(
    csv_file,
    minimal_payload,
    tmp_path,
    settings,
):
    """process_file_import returns the id of the created FileImport record."""
    settings.MEDIA_ROOT = tmp_path

    result = process_file_import(csv_file, minimal_payload)

    assert isinstance(result, int)
    assert FileImport.objects.filter(id=result).exists()


@pytest.mark.django_db
@pytest.mark.service
def test_process_file_import_with_transactions(
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_checking_account,
    test_tag,
    tmp_path,
    settings,
):
    """process_file_import correctly creates TransactionImport rows for each transaction in the payload."""
    settings.MEDIA_ROOT = tmp_path

    csv_file = SimpleUploadedFile(
        "with_transactions.csv",
        b"id,amount,date\n1,50,2026-01-15\n",
        content_type="text/csv",
    )

    payload = MappingDefinition(
        transaction_types=[
            TypeMappingSchema(
                file_type="Expense",
                type_id=test_expense_transaction_type.id,
            )
        ],
        transaction_statuses=[
            StatusMappingSchema(
                file_status="Pending",
                status_id=test_pending_transaction_status.id,
            )
        ],
        accounts=[
            AccountMappingSchema(
                file_account="Checking",
                account_id=test_checking_account.id,
            )
        ],
        tags=[
            TagMappingSchema(
                file_tag="Groceries",
                tag_id=test_tag.id,
            )
        ],
        transactions=[
            TransactionImportSchema(
                line_id=1,
                transactionDate=date(2026, 1, 15),
                transactionTypeID=test_expense_transaction_type.id,
                transactionStatusID=test_pending_transaction_status.id,
                amount="50.00",
                description="Test import transaction",
                sourceAccountID=test_checking_account.id,
                destinationAccountID=None,
                tags=[],
                memo="",
                errors=[],
            )
        ],
    )

    file_import_id = process_file_import(csv_file, payload)

    from imports.models import TransactionImport
    assert TransactionImport.objects.filter(file_import_id=file_import_id).count() == 1
    created = TransactionImport.objects.get(file_import_id=file_import_id)
    assert created.description == "Test import transaction"
    assert created.line_id == 1
