from administration.models import Message
from imports.models import (
    FileImport,
    TransactionImport,
    TransactionImportTag,
    TransactionImportError,
    TypeMapping,
    StatusMapping,
    AccountMapping,
    TagMapping,
)
from utils.dates import get_todays_date_timezone_adjusted


def process_file_import(import_file, payload) -> int:
    imported_file = FileImport.objects.create(import_file=import_file)

    for type_mapping in payload.transaction_types:
        TypeMapping.objects.create(
            file_type=type_mapping.file_type,
            type_id=type_mapping.type_id,
            file_import=imported_file,
        )
    for status_mapping in payload.transaction_statuses:
        StatusMapping.objects.create(
            file_status=status_mapping.file_status,
            status_id=status_mapping.status_id,
            file_import=imported_file,
        )
    for account_mapping in payload.accounts:
        AccountMapping.objects.create(
            file_account=account_mapping.file_account,
            account_id=account_mapping.account_id,
            file_import=imported_file,
        )
    for tag_mapping in payload.tags:
        TagMapping.objects.create(
            file_tag=tag_mapping.file_tag,
            tag_id=tag_mapping.tag_id,
            file_import=imported_file,
        )
    for transaction in payload.transactions:
        created_transaction = TransactionImport.objects.create(
            line_id=transaction.line_id,
            transaction_date=transaction.transactionDate,
            transaction_type_id=transaction.transactionTypeID,
            transaction_status_id=transaction.transactionStatusID,
            amount=transaction.amount,
            description=transaction.description,
            source_account_id=transaction.sourceAccountID,
            destination_account_id=transaction.destinationAccountID,
            memo=transaction.memo,
            file_import=imported_file,
        )
        for tag in transaction.tags:
            TransactionImportTag.objects.create(
                tag_id=tag.tag_id,
                tag_name=tag.tag_name,
                tag_amount=tag.tag_amount,
                transaction_import=created_transaction,
            )
        for error in transaction.errors:
            TransactionImportError.objects.create(
                text=error.text,
                status=error.status,
                transaction_import=created_transaction,
            )

    Message.objects.create(
        message_date=get_todays_date_timezone_adjusted(True),
        message=f"File import ID #{imported_file.id} started",
        unread=True,
    )
    return imported_file.id
