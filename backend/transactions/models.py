"""
Module: models.py
Description: Contains django model definitions.

Author: John Adams <johnmadams96@gmail.com>
Date: February 15, 2024
"""

from django.db import models
from datetime import date
from django.utils import timezone
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.db.models import Case, When, Q, Value, IntegerField
from decimal import Decimal
import datetime
from typing import List
from django.db import IntegrityError, connection, transaction
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet
from accounts.models import Account
from tags.models import Tag
from administration.models import LogEntry, Option, logToDB
import pytz
import os


def transaction_image_name(instance, filename):
    timestamp = timezone.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"tran_images/{timestamp}-{filename}"


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    return today_tz


# Create your models here.


class TransactionType(models.Model):
    """
    Model representing a transaction type to determine the type of transaction.

    Fields:
    - transaction_type (CharField): The name of the transaction type, limited to 254 characters,
    and must be unique.
    """

    transaction_type = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.transaction_type


class TransactionStatus(models.Model):
    """
    Model representing a transactions status.

    Fields:
    - transaction_status (CharField): The transaction status, limited to 254 characters
    """

    transaction_status = models.CharField(max_length=254, unique=True)

    class Meta:
        verbose_name_plural = "Transaction statuses"

    def __str__(self):
        return self.transaction_status


class Paycheck(models.Model):
    """
    Model representing a paycheck.

    Fields:
    - gross (DecimalField): The gross amount of the paycheck, default is 0.00.
    - net (DecimalField): The net amount of the paycheck, default is 0.00.
    - taxes (DecimalField): The taxes of the paycheck, default is 0.00.
    - health (DecimalField): The total health deduction of the paycheck, default is 0.00.
    - pension (DecimalField): The pension deduction of the paycheck, default is 0.00.
    - fsa (DecimalField): The FSA deduction of the paycheck, default is 0.00.
    - dca (DecimalField): The DCA deduction of the paycheck, default is 0.00.
    - union_dues (DecimalField): The union dues deduction of the paycheck, default is 0.00.
    - four_fifty_seven_b (DecimalField): The 457b deduction of the paycheck, default is 0.00.
    - payee (ForeignKey): A reference to the Payee model, representing the payee of the paycheck.
    """

    gross = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    taxes = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    health = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    pension = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    fsa = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    dca = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    union_dues = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    four_fifty_seven_b = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    payee = models.ForeignKey(
        "administration.Payee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )


class Transaction(models.Model):
    """
    Model representing a transaction.

    Fields:
    - transaction_date (DateField): The date of the transaction, defaults to today.
    - total_amount (DecimalField): The total amount of the transaction, default is 0.00.
    - status (ForeignKey): A reference to the TransactionStatus model, representing the
    status of the transaction.
    - memo (CharField): A memo to document this transaction, limited to 254 characters.
    - description (CharField): A description of this description, limited to 254 characters.
    - edit_date (DateField): The last date this transacion was edited, defaults to today.
    - add_date (DateField): The date this transaction was added, defaults to today.
    - transaction_type (ForeignKey): A reference to the TransactionType model, representing
    the type of this transaction.
    - paycheck (ForeignKey): A reference to the Paycheck model, representing a paycheck
    associated with this transaction.  Default is None, and is Optional.
    - checkNumber (IntegerField): Number of a check associated with this transaction. Default
    is None, and is Optional.
    - sourceAccount (ForeignKey): A reference to Account model, representing the source account.
    - destinationAccount (ForeignKey): A reference to Account model, representing the destination
    account.
    """

    transaction_date = models.DateField(default=current_date)
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    status = models.ForeignKey(
        TransactionStatus, on_delete=models.SET_NULL, null=True, blank=True
    )
    memo = models.CharField(max_length=508, null=True, blank=True, default=None)
    description = models.CharField(max_length=254)
    edit_date = models.DateField(default=current_date)
    add_date = models.DateField(default=current_date)
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    paycheck = models.ForeignKey(
        Paycheck,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    checkNumber = models.IntegerField(null=True, blank=True, default=None)
    source_account = models.ForeignKey(
        Account,
        related_name="source_transactions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    destination_account = models.ForeignKey(
        Account,
        related_name="destination_transactions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return f"#{self.id} | {self.transaction_date} : {self.description} (${self.total_amount})"


class TransactionImage(models.Model):
    """
    Model representing a transaction image.

    Fields:
    - image (ImageField): The image.
    - transaction (ForeignKey): A reference to the Transaction model, associating the
    transaction with this image.
    """

    image = models.FileField(upload_to=transaction_image_name)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        # Delete the associated file when the instance is deleted
        self.image.delete()
        super().delete(*args, **kwargs)


class TransactionDetail(models.Model):
    """
    Model representing a transaction detail, that combined with an associated
    transaction, represents a full transaction.

    Fields:
    - transaction (ForeignKey): A reference to the Transaction model, representing
    the transaction associated with this transaction detail.
    - detail_amt (DecimalField): The amount associated with this transaction detail,
    default is 0.00.
    - tag (ForeignKey): A refernce to the Tag model, representing the tag category
    ot this transaction detail.
    """

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    detail_amt = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.SET_NULL, null=True, blank=True
    )


class CustomTag:
    def __init__(self, tag_name: str, tag_amount: float, tag_id: int):
        self.tag_name = tag_name
        self.tag_amount = tag_amount
        self.tag_id = tag_id

    def __str__(self):
        return (
            f"CustomTag(tag_name={self.tag_name}, "
            f"tag_amount={self.tag_amount}, "
            f"tag_id={self.tag_id})"
        )


class FullTransaction:

    def __init__(
        self,
        transaction_date: datetime.date,
        total_amount: float,
        status_id: int,
        memo: str,
        description: str,
        edit_date: datetime.date,
        add_date: datetime.date,
        transaction_type_id: int,
        paycheck_id: int,
        source_account_id: int,
        destination_account_id: int,
        tags: List[CustomTag],
        checkNumber: int,
    ):
        self.transaction_date = transaction_date
        self.total_amount = total_amount
        self.status_id = status_id
        self.memo = memo
        self.description = description
        self.edit_date = edit_date
        self.add_date = add_date
        self.transaction_type_id = transaction_type_id
        self.paycheck_id = paycheck_id
        self.source_account_id = source_account_id
        self.destination_account_id = destination_account_id
        self.tags = tags
        self.checkNumber = checkNumber

    def __str__(self):
        return (
            f"FullTransaction(transaction_date={self.transaction_date}, "
            + f"total_amount={self.total_amount}, "
            + f"status_id={self.status_id}, "
            + f"memo={self.memo}, "
            + f"description={self.description}, "
            + f"edit_date={self.edit_date}, "
            + f"add_date={self.add_date}, "
            + f"transaction_type_id={self.transaction_type_id}, "
            + f"paycheck_id={self.paycheck_id}, "
            + f"source_account_id={self.source_account_id}, "
            + f"destination_account_id={self.destination_account_id}, "
            + f"tags={self.tags}, "
            + f"checkNumber={self.checkNumber})"
        )


def create_transactions(transactions: List[FullTransaction]):
    """
    The function `create_transactions` creates transactions either individually
    or using bulk_create based on paramters.

    Args:
        transactions (List[FullTransaction]): a list of at least 1 transaction to create
    Returns:
        bool: Returns true or false depending on success
    """

    # Initiate variables...
    max_bulk = 1000  # Chunk size for bulk record creations
    bulk_lower_limit = 10  # Lower limit to process as bulk_create

    # Define how to break up records into chunks
    def chunk_list(lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i : i + chunk_size]

    # Determine wether to process as individual creations or use bulk_create
    if len(transactions) <= bulk_lower_limit:
        with transaction.atomic():
            try:
                for trans in transactions:
                    try:
                        if trans.transaction_type_id == 1:
                            amount = -abs(trans.total_amount)
                        elif trans.transaction_type_id == 2:
                            amount = abs(trans.total_amount)
                        elif trans.transaction_type_id == 3:
                            amount = -abs(trans.total_amount)
                        created_transaction = Transaction.objects.create(
                            transaction_date=trans.transaction_date,
                            total_amount=amount,
                            status_id=trans.status_id,
                            memo=trans.memo,
                            description=trans.description,
                            edit_date=trans.edit_date,
                            add_date=trans.add_date,
                            transaction_type_id=trans.transaction_type_id,
                            paycheck_id=trans.paycheck_id,
                            source_account_id=trans.source_account_id,
                            destination_account_id=trans.destination_account_id,
                            checkNumber=trans.checkNumber,
                        )
                        try:
                            if trans.tags and len(trans.tags) != 0:
                                for tag in trans.tags:
                                    adj_amount = 0
                                    if trans.transaction_type_id == 1:
                                        adj_amount = -abs(tag.tag_amount)
                                    else:
                                        adj_amount = abs(tag.tag_amount)
                                    TransactionDetail.objects.create(
                                        transaction_id=created_transaction.id,
                                        detail_amt=adj_amount,
                                        tag_id=tag.tag_id,
                                    )
                        except Except as e:
                            logToDB(
                                f"Transaction detail creation error: {e}",
                                None,
                                None,
                                None,
                                3001901,
                                2,
                            )
                    except Exception as e:
                        logToDB(
                            f"Transaction creation error: {e}",
                            None,
                            None,
                            None,
                            3001901,
                            2,
                        )
                logToDB(
                    "Transaction(s) created successfully",
                    None,
                    None,
                    None,
                    3001001,
                    1,
                )
                return True
            except Exception as e:
                print(f"Unable to create transaction(s): {e}")
                transaction.rollback()
                logToDB(
                    f"Transaction(s) not created: {e}",
                    None,
                    None,
                    None,
                    3001901,
                    2,
                )
                return False
    else:
        try:
            transactions_to_create = []
            transfers_to_create = []
            related_to_create = []
            transaction_details = []
            transfer_transaction_details = []
            related_transaction_details = []
            details_to_create = []
            created_transactions = []
            created_transfers = []
            created_related = []
            transactions_to_update = []
            for index, trans in enumerate(transactions):
                if trans.transaction_type_id == 1:
                    amount = -abs(trans.total_amount)
                elif trans.transaction_type_id == 2:
                    amount = abs(trans.total_amount)
                elif trans.transaction_type_id == 3:
                    amount = -abs(trans.total_amount)
                trans_obj = Transaction(
                    transaction_date=trans.transaction_date,
                    total_amount=amount,
                    status_id=trans.status_id,
                    memo=trans.memo,
                    description=trans.description,
                    edit_date=trans.edit_date,
                    add_date=trans.add_date,
                    transaction_type_id=trans.transaction_type_id,
                    paycheck_id=trans.paycheck_id,
                    source_account_id=trans.source_account_id,
                    destination_account_id=trans.destination_account_id,
                    checkNumber=trans.checkNumber,
                )
                transactions_to_create.append(trans_obj)
                if trans.tags and len(trans.tags) != 0:
                    for tag in trans.tags:
                        adj_amount = 0
                        if trans.transaction_type_id == 1:
                            adj_amount = -abs(tag.tag_amount)
                        else:
                            adj_amount = abs(tag.tag_amount)
                        detail_dict = {
                            "transaction_index": index,
                            "detail_amt": adj_amount,
                            "tag_id": tag.tag_id,
                        }
                        transaction_details.append(detail_dict)
            # Create transactions
            try:
                chunks = list(chunk_list(transactions_to_create, max_bulk))
                for step, chunk in enumerate(chunks, start=0):
                    created_transactions.extend(
                        Transaction.objects.bulk_create(chunk)
                    )
                logToDB(
                    "Transaction chunks created successfully",
                    None,
                    None,
                    None,
                    3001001,
                    1,
                )
            except Exception as e:
                logToDB(
                    f"Transaction chunks not created: {e}",
                    None,
                    None,
                    None,
                    3001901,
                    2,
                )
            # Create transaction details
            for trans_detail in transaction_details:
                detail = TransactionDetail(
                    transaction_id=created_transactions[
                        trans_detail.transaction_index
                    ]["id"],
                    detail_amt=trans_detail.detail_amt,
                    tag_id=trans_detail.tag_id,
                )
                details_to_create.append(detail)
            try:
                chunks = list(chunk_list(details_to_create, max_bulk))
                for step, chunk in enumerate(chunks, start=0):
                    TransactionDetail.objects.bulk_create(chunk)
                logToDB(
                    "Transaction detail chunks created successfully",
                    None,
                    None,
                    None,
                    3001001,
                    1,
                )
            except Exception as e:
                logToDB(
                    f"Transaction detail chunks not created: {e}",
                    None,
                    None,
                    None,
                    3001901,
                    2,
                )
            logToDB(
                "Transaction(s) created successfully",
                None,
                None,
                None,
                3001001,
                1,
            )
            # update_running_totals()
            return True
        except Exception as e:
            logToDB(
                f"Transaction(s) not created: {e}",
                None,
                None,
                None,
                3001901,
                2,
            )
            return False


def sort_transactions(
    transactions: QuerySet[Transaction],
    asc: bool = True,
):
    """
    The function `sort_transactions` returns the provided transactions sorted.

    Args:
        transactions (QuerySet[Transaction]): A list of transactions to sort
        asc (bool): Perform a full (all objects) sort order update
    Returns:
        QuerySet[Transaction]: Sorted QuerySet of Transaction objects.
    """
    if asc:
        transactions = transactions.annotate(
            custom_order=Case(
                When(status_id=1, then=Value(2)),
                When(status_id=2, then=Value(0)),
                When(status_id=3, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by(
            "custom_order",
            "transaction_date",
            "-total_amount",
            "id",
        )
    else:
        transactions = transactions.annotate(
            custom_order=Case(
                When(status_id=1, then=Value(2)),
                When(status_id=2, then=Value(0)),
                When(status_id=3, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by(
            "-custom_order",
            "-transaction_date",
            "total_amount",
            "-id",
        )

    return transactions
