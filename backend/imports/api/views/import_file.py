from ninja import Router, Query, File
from ninja.files import UploadedFile
from django.db import IntegrityError
from ninja.errors import HttpError
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
from imports.api.schemas.import_file import (
    AccountMappingSchema,
    TypeMappingSchema,
    StatusMappingSchema,
    TagMappingSchema,
    TransactionImportErrorSchema,
    TransactionImportSchema,
    TransactionImportTagSchema,
    MappingDefinition,
)
from administration.api.dependencies.log_to_db import logToDB
from django.shortcuts import get_object_or_404
from typing import List
from django.db.models import (
    Case,
    When,
    Q,
    IntegerField,
    Value,
    F,
    CharField,
    Sum,
    Subquery,
    OuterRef,
    FloatField,
    Window,
    ExpressionWrapper,
    DecimalField,
    Func,
    Count,
)
from django.db.models.functions import Concat, Coalesce, Abs
from typing import List, Optional, Dict, Any
import pytz
import os
from django.utils import timezone
from administration.api.dependencies.get_todays_date_timezone_adjusted import (
    get_todays_date_timezone_adjusted,
)

import_file_router = Router(tags=["File Imports"])


@import_file_router.post("/create")
def import_file(
    request,
    payload: MappingDefinition,
    import_file: UploadedFile = File(...),
):
    """
    The function `import_file` uploads an import file and its mapping definition.

    Args:
        request (HttpRequest): The HTTP request object.
        payload (MappingDefinition): the mapping definition for the import
        import_file (File): the import file to upload in csv format

    Returns:
        success: True
    """
    try:
        importedFile = FileImport.objects.create(import_file=import_file)
        for type_mapping in payload.transaction_types:
            TypeMapping.objects.create(
                file_type=type_mapping.file_type,
                type_id=type_mapping.type_id,
                file_import=importedFile,
            )
        for status_mapping in payload.transaction_statuses:
            StatusMapping.objects.create(
                file_status=status_mapping.file_status,
                status_id=status_mapping.status_id,
                file_import=importedFile,
            )
        for account_mapping in payload.accounts:
            AccountMapping.objects.create(
                file_account=account_mapping.file_account,
                account_id=account_mapping.account_id,
                file_import=importedFile,
            )
        for tag_mapping in payload.tags:
            TagMapping.objects.create(
                file_tag=tag_mapping.file_tag,
                tag_id=tag_mapping.tag_id,
                file_import=importedFile,
            )
        for transaction in payload.transactions:
            createTransaction = TransactionImport.objects.create(
                line_id=transaction.line_id,
                transaction_date=transaction.transactionDate,
                transaction_type_id=transaction.transactionTypeID,
                transaction_status_id=transaction.transactionStatusID,
                amount=transaction.amount,
                description=transaction.description,
                source_account_id=transaction.sourceAccountID,
                destination_account_id=transaction.destinationAccountID,
                memo=transaction.memo,
                file_import=importedFile,
            )
            for tag in transaction.tags:
                TransactionImportTag.objects.create(
                    tag_id=tag.tag_id,
                    tag_name=tag.tag_name,
                    tag_amount=tag.tag_amount,
                    transaction_import=createTransaction,
                )
            for error in transaction.errors:
                TransactionImportError.objects.create(
                    text=error.text,
                    status=error.status,
                    transaction_import=createTransaction,
                )
        Message.objects.create(
            message_date=get_todays_date_timezone_adjusted(True),
            message=f"File import ID #{importedFile.id} started",
            unread=True,
        )
        logToDB(
            f"File import ID #{importedFile.id} started",
            None,
            None,
            None,
            3002001,
            2,
        )
        return {"id": importedFile.id}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"File import failed : {str(e)}",
            None,
            None,
            None,
            3002901,
            3,
        )
        raise HttpError(500, "File import error")
