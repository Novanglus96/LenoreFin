from django.db import models
from datetime import date
from django.utils import timezone
from django.db.models import Case, When, Q, Value, IntegerField
from decimal import Decimal
import datetime
from typing import List
from django.db import IntegrityError, connection, transaction
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet

# Create your models here.


def import_file_name(instance, filename):
    timestamp = timezone.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"imports/import-{timestamp}.csv"


def mapping_file_name(instance, filename):
    timestamp = timezone.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"imports/mapping-{timestamp}.csv"


class FileImport(models.Model):
    """
    Model representing a file import to import transactions.

    Fields:
    - import_file (FileField): The transcation import file.
    - processed (BooleanField): True if this file has been processed.
    - successful (BooleanField): True if the import was successful.
    - errors (IntegerField): Number of errors encountered during import.
    """

    import_file = models.FileField(upload_to=import_file_name)
    processed = models.BooleanField(default=False)
    successful = models.BooleanField(null=True, blank=True, default=None)
    errors = models.IntegerField(default=0)

    def delete(self, *args, **kwargs):
        # Delete the associated file when the instance is deleted
        self.import_file.delete()
        super().delete(*args, **kwargs)


class TransactionImport(models.Model):
    """
    Model representing a transaction import.

    Fields:
    - line_id (Integer): The import line # of the transaction.
    - transaction_date (DateField): The date of the transaction.
    - transaction_type_id (Integer): The ID of the corresponding type
    - transaction_status_id (Integer): The ID of the corresponding status
    - amount (Decimal): The amount of the transaction
    - description (CharField): The description of the transaction
    - source_account_id (Integer): The ID of the corresponding account
    - destination_account_id (Integer): The ID of the corresponding account
    - memo (CharField): Transaction memo
    - file_import (FileImport): The file import associated with this mapping.
    """

    line_id = models.IntegerField()
    transaction_date = models.DateField()
    transaction_type_id = models.IntegerField()
    transaction_status_id = models.IntegerField()
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=True
    )
    description = models.CharField(max_length=254)
    source_account_id = models.IntegerField()
    destination_account_id = models.IntegerField(default=None, null=True)
    memo = models.TextField()
    file_import = models.ForeignKey(FileImport, on_delete=models.CASCADE)


class TransactionImportTag(models.Model):
    """
    Model representing a transaction import tag.

    Fields:
    - tag_id (Integer): The ID of the corresponding tag.
    - tag_name (CharField): The tag name.
    - tag_amount (Decimal): The amount of the tag.
    - transaction_import (TransactionImport): The associated transaction import.
    """

    tag_id = models.IntegerField()
    tag_name = models.CharField(max_length=254)
    tag_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=True
    )
    transaction_import = models.ForeignKey(
        TransactionImport, on_delete=models.CASCADE
    )


class TransactionImportError(models.Model):
    """
    Model representing a transaction import error.

    Fields:
    - text (CharField): The text of the error.
    - status (Integer): The status of the error.
    - transaction_import (TransactionImport): The associated transaction import.
    """

    text = models.CharField(max_length=254)
    status = models.IntegerField()
    transaction_import = models.ForeignKey(
        TransactionImport, on_delete=models.CASCADE
    )


class TypeMapping(models.Model):
    """
    Model representing a mapping for transaction types.

    Fields:
    - file_type (CharField): The type as defined in the import file.
    - type_id (Integer): The ID of the corresponding type.
    - file_import (FileImport): The file import associated with this mapping.
    """

    file_type = models.CharField(max_length=254)
    type_id = models.IntegerField()
    file_import = models.ForeignKey(FileImport, on_delete=models.CASCADE)


class StatusMapping(models.Model):
    """
    Model representing a mapping for transaction statuses.

    Fields:
    - file_status (CharField): The status as defined in the import file.
    - status_id (Integer): The ID of the corresponding status.
    - file_import (FileImport): The file import associated with this mapping.
    """

    file_status = models.CharField(max_length=254)
    status_id = models.IntegerField()
    file_import = models.ForeignKey(FileImport, on_delete=models.CASCADE)


class AccountMapping(models.Model):
    """
    Model representing a mapping for accounts.

    Fields:
    - file_account (CharField): The account as defined in the import file.
    - account_id (Integer): The ID of the corresponding account.
    - file_import (FileImport): The file import associated with this mapping.
    """

    file_account = models.CharField(max_length=254)
    account_id = models.IntegerField()
    file_import = models.ForeignKey(FileImport, on_delete=models.CASCADE)


class TagMapping(models.Model):
    """
    Model representing a mapping for tags.

    Fields:
    - file_tag (CharField): The tag as defined in the import file.
    - tag_id (Integer): The ID of the corresponding tag.
    - file_import (FileImport): The file import associated with this mapping.
    """

    file_tag = models.CharField(max_length=254)
    tag_id = models.IntegerField()
    file_import = models.ForeignKey(FileImport, on_delete=models.CASCADE)
