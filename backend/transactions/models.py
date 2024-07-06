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


updating_related_transaction = False


@receiver(post_save, sender=Transaction)
def update_related_transactions(sender, instance, created, **kwargs):
    """
    Signal receiver function to update related transactions when a Transaction is saved.
    """
    print(f"Starting update_related_transaction: {instance.id}")
    global updating_related_transaction
    if not updating_related_transaction:
        updating_related_transaction = True
        try:
            # Check if the saved transaction is a transfer
            if instance.transaction_type.id == 3:
                related_transaction = None
                # Get the related transaction
                if instance.related_transaction:
                    related_transaction = Transaction.objects.get(
                        id=instance.related_transaction.id
                    )
                # Update the related transaction based on the changes in the current transaction
                if instance.related_transaction.id < instance.id:
                    related_transaction.total_amount = -abs(
                        instance.total_amount
                    )
                    related_transaction.account_id = instance.source_account_id
                    detail = TransactionDetail.objects.filter(
                        transaction_id=related_transaction.id
                    ).first()
                    detail.account_id = instance.source_account_id
                    detail.detail_amt = -abs(instance.total_amount)
                    detail.save()
                else:
                    related_transaction.total_amount = abs(
                        instance.total_amount
                    )
                    related_transaction.account_id = (
                        instance.destination_account_id
                    )
                    detail = TransactionDetail.objects.filter(
                        transaction_id=related_transaction.id
                    ).first()
                    detail.account_id = instance.destination_account_id
                    detail.detail_amt = abs(instance.total_amount)
                    detail.save()
                related_transaction.transaction_date = instance.transaction_date
                related_transaction.status_id = instance.status_id
                related_transaction.memo = instance.memo
                related_transaction.description = instance.description
                related_transaction.edit_date = timezone.now()
                related_transaction.souce_account_id = (
                    instance.source_account_id
                )
                related_transaction.destination_account_id = (
                    instance.destination_account_id
                )
                related_transaction.save()
                updating_related_transaction = False
                logToDB(
                    "Updated related transaction",
                    None,
                    None,
                    related_transaction.id,
                    3001002,
                    1,
                )
        except Exception as e:
            updating_related_transaction = False
            logToDB(
                f"Updating related transaction error: {e}",
                None,
                None,
                None,
                3001902,
                2,
            )
    else:
        print(f"Not updating related transaction: {instance.id}")


updating_running_totals = False


@receiver(post_save, sender=Transaction)
@receiver(pre_delete, sender=Transaction)
def update_sort_totals(sender, instance, **kwargs):
    global updating_running_totals  # Declare the variable as global
    if not updating_running_totals:
        updating_running_totals = True
        obj_list = []
        obj_list.append(instance)
        try:
            if kwargs.get("signal") == pre_delete:
                update_running_totals(False, True, obj_list)
            else:
                update_running_totals(False, False, obj_list)
        except Exception as e:
            print(f"Failed to update running totals: {e}")
            updating_running_totals = False
        updating_running_totals = False


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
        reminder_id: int,
        paycheck_id: int,
        source_account_id: int,
        destination_account_id: int,
        tags: List[CustomTag],
    ):
        self.transaction_date = transaction_date
        self.total_amount = total_amount
        self.status_id = status_id
        self.memo = memo
        self.description = description
        self.edit_date = edit_date
        self.add_date = add_date
        self.transaction_type_id = transaction_type_id
        self.reminder_id = reminder_id
        self.paycheck_id = paycheck_id
        self.source_account_id = source_account_id
        self.destination_account_id = destination_account_id
        self.tags = tags

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
            + f"reminder_id={self.reminder_id}, "
            + f"paycheck_id={self.paycheck_id}, "
            + f"source_account_id={self.source_account_id}, "
            + f"destination_account_id={self.destination_account_id}, "
            + f"tags={self.tags})"
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
                        account_id = trans.source_account_id
                        source_account_id = None
                        destination_account_id = None
                        if trans.transaction_type_id == 1:
                            amount = -abs(trans.total_amount)
                        elif trans.transaction_type_id == 2:
                            amount = abs(trans.total_amount)
                        elif trans.transaction_type_id == 3:
                            source_account_id = trans.source_account_id
                            destination_account_id = (
                                trans.destination_account_id
                            )
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
                            reminder_id=trans.reminder_id,
                            paycheck_id=trans.paycheck_id,
                            account_id=account_id,
                            source_account_id=source_account_id,
                            destination_account_id=destination_account_id,
                        )
                        try:
                            if trans.transaction_type_id == 3:
                                related_transaction = Transaction.objects.create(
                                    transaction_date=trans.transaction_date,
                                    total_amount=abs(amount),
                                    status_id=trans.status_id,
                                    memo=trans.memo,
                                    description=trans.description,
                                    edit_date=trans.edit_date,
                                    add_date=trans.add_date,
                                    transaction_type_id=trans.transaction_type_id,
                                    reminder_id=trans.reminder_id,
                                    paycheck_id=trans.paycheck_id,
                                    account_id=destination_account_id,
                                    source_account_id=source_account_id,
                                    destination_account_id=destination_account_id,
                                    related_transaction=created_transaction,
                                )
                                created_transaction.related_transaction = (
                                    related_transaction
                                )
                                created_transaction.save()
                                TransactionDetail.objects.create(
                                    transaction_id=created_transaction.id,
                                    account_id=trans.source_account_id,
                                    detail_amt=amount,
                                    tag_id=2,
                                )
                                TransactionDetail.objects.create(
                                    transaction_id=related_transaction.id,
                                    account_id=trans.destination_account_id,
                                    detail_amt=abs(amount),
                                    tag_id=2,
                                )
                            else:
                                if trans.tags and len(trans.tags) != 0:
                                    for tag in trans.tags:
                                        adj_amount = 0
                                        if trans.transaction_type_id == 1:
                                            adj_amount = -abs(tag.tag_amount)
                                        else:
                                            adj_amount = abs(tag.tag_amount)
                                        TransactionDetail.objects.create(
                                            transaction_id=created_transaction.id,
                                            account_id=trans.source_account_id,
                                            detail_amt=adj_amount,
                                            tag_id=tag.tag_id,
                                        )
                                else:
                                    TransactionDetail.objects.create(
                                        transaction_id=created_transaction.id,
                                        account_id=trans.source_account_id,
                                        detail_amt=amount,
                                        tag_id=1,
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
            for trans in transactions:
                account_id = trans.source_account_id
                source_account_id = None
                destination_account_id = None
                if trans.transaction_type_id == 1:
                    amount = -abs(trans.total_amount)
                elif trans.transaction_type_id == 2:
                    amount = abs(trans.total_amount)
                elif trans.transaction_type_id == 3:
                    source_account_id = trans.source_account_id
                    destination_account_id = trans.destination_account_id
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
                    reminder_id=trans.reminder_id,
                    paycheck_id=trans.paycheck_id,
                    account_id=account_id,
                    source_account_id=source_account_id,
                    destination_account_id=destination_account_id,
                )
                if trans.transaction_type_id == 3:
                    transfers_to_create.append(trans_obj)
                    transfer_detail_dict = {
                        "account_id": trans.source_account_id,
                        "tags": trans.tags,
                        "type_id": trans.transaction_type_id,
                        "total_amount": amount,
                    }
                    transfer_transaction_details.append(transfer_detail_dict)
                    related_obj = Transaction(
                        transaction_date=trans.transaction_date,
                        total_amount=abs(amount),
                        status_id=trans.status_id,
                        memo=trans.memo,
                        description=trans.description,
                        edit_date=trans.edit_date,
                        add_date=trans.add_date,
                        transaction_type_id=trans.transaction_type_id,
                        reminder_id=trans.reminder_id,
                        paycheck_id=trans.paycheck_id,
                        account_id=destination_account_id,
                        source_account_id=source_account_id,
                        destination_account_id=destination_account_id,
                    )
                    related_to_create.append(related_obj)
                    related_detail_dict = {
                        "account_id": trans.destination_account_id,
                        "tags": trans.tags,
                        "type_id": trans.transaction_type_id,
                        "total_amount": abs(amount),
                    }
                    related_transaction_details.append(related_detail_dict)
                else:
                    transactions_to_create.append(trans_obj)
                    detail_dict = {
                        "account_id": trans.source_account_id,
                        "tags": trans.tags,
                        "type_id": trans.transaction_type_id,
                        "total_amount": trans.total_amount,
                    }
                    transaction_details.append(detail_dict)
            # Create non transfer transactions
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
            # Create transfer transactions
            try:
                chunks = list(chunk_list(transfers_to_create, max_bulk))
                for step, chunk in enumerate(chunks, start=0):
                    created_transfers.extend(
                        Transaction.objects.bulk_create(chunk)
                    )
                logToDB(
                    "Transfer chunks created successfully",
                    None,
                    None,
                    None,
                    3001001,
                    1,
                )
            except Exception as e:
                logToDB(
                    f"Transfer chunks not created: {e}",
                    None,
                    None,
                    None,
                    3001901,
                    2,
                )
            # Create related transactions
            for index, obj in enumerate(related_to_create):
                obj.related_transaction = created_transfers[index]
            try:
                chunks = list(chunk_list(related_to_create, max_bulk))
                for step, chunk in enumerate(chunks, start=0):
                    created_related.extend(
                        Transaction.objects.bulk_create(chunk)
                    )
                logToDB(
                    "Related chunks created successfully",
                    None,
                    None,
                    None,
                    3001001,
                    1,
                )
            except Exception as e:
                logToDB(
                    f"Related chunks not created: {e}",
                    None,
                    None,
                    None,
                    3001901,
                    2,
                )
            # Update created transfers
            for index, obj in enumerate(created_transfers):
                obj.related_transaction = created_related[index]
                transactions_to_update.append(obj)
            Transaction.objects.bulk_update(
                transactions_to_update,
                ["related_transaction"],
                batch_size=1000,
            )
            # Create transaction details
            for index, obj in enumerate(created_transactions):
                if (
                    transaction_details[index]["tags"]
                    and len(transaction_details[index]["tags"]) != 0
                ):
                    for tag in transaction_details[index]["tags"]:
                        adj_amount = 0
                        if transaction_details[index]["type_id"] == 1:
                            adj_amount = -abs(tag.tag_amount)
                        else:
                            adj_amount = abs(tag.tag_amount)
                        detail = TransactionDetail(
                            transaction_id=obj.id,
                            account_id=transaction_details[index]["account_id"],
                            detail_amt=adj_amount,
                            tag_id=tag.tag_id,
                        )
                        details_to_create.append(detail)
                else:
                    detail = TransactionDetail(
                        transaction_id=obj.id,
                        account_id=transaction_details[index]["account_id"],
                        detail_amt=transaction_details[index]["total_amount"],
                        tag_id=1,
                    )
                    details_to_create.append(detail)
            # Create transfer details
            for index, obj in enumerate(created_transfers):
                detail = TransactionDetail(
                    transaction_id=obj.id,
                    account_id=transfer_transaction_details[index][
                        "account_id"
                    ],
                    detail_amt=transfer_transaction_details[index][
                        "total_amount"
                    ],
                    tag_id=2,
                )
                details_to_create.append(detail)
            for index, obj in enumerate(created_related):
                detail = TransactionDetail(
                    transaction_id=obj.id,
                    account_id=related_transaction_details[index]["account_id"],
                    detail_amt=related_transaction_details[index][
                        "total_amount"
                    ],
                    tag_id=2,
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
            update_running_totals()
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


def update_running_totals(
    full: bool = True,
    delete: bool = False,
    transactions: List[Transaction] = [],
):
    """
    The function `update_running_totals` updates the running totals.

    Args:
        full (bool): Perform a full (all objects) running total update
        delete (bool): Is this update a result of a deletion
        transactions (List[Transaction]): A list of transactions to update

    Returns:
        bool: True or False depending on status
    """
    try:
        # Perform a full update
        if full or len(transactions) > 0:
            try:
                account_ids = [
                    obj.account_id
                    for obj in transactions
                    if obj.account_id is not None
                ]
                dest_ids = [
                    obj.destination_account_id
                    for obj in transactions
                    if obj.destination_account_id is not None
                ]
                source_ids = [
                    obj.source_account_id
                    for obj in transactions
                    if obj.source_account_id is not None
                ]
                combined_ids = account_ids + dest_ids + source_ids
                unique_account_ids = set(combined_ids)
                affected_accounts = list(unique_account_ids)
                print(f"accounts: {affected_accounts}")
                balances = []
                accounts = None
                transactions = None
                if full:
                    accounts = Account.objects.all().order_by("id")
                    transactions = sort_transactions(Transaction.objects.all())
                else:
                    accounts = Account.objects.filter(
                        id__in=affected_accounts
                    ).order_by("id")
                    transactions = sort_transactions(
                        Transaction.objects.filter(
                            account_id__in=affected_accounts
                        )
                    )
                for account in accounts:
                    bal_obj = {
                        "id": account.id,
                        "balance": account.opening_balance,
                    }
                    balances.append(bal_obj)
                transactions_to_update = []
                for trans in transactions:
                    trans_total = Decimal(0)
                    # Find matching source account in balances
                    source_account = next(
                        (
                            bal
                            for bal in balances
                            if bal["id"] == trans.account_id
                        ),
                        None,
                    )
                    if source_account:
                        # Update transaction and balance object
                        source_account["balance"] += trans.total_amount
                        trans_total = source_account["balance"]
                    trans_instance = Transaction(
                        id=trans.id,
                        running_total=trans_total,
                    )
                    transactions_to_update.append(trans_instance)
                try:
                    Transaction.objects.bulk_update(
                        transactions_to_update,
                        ["running_total"],
                        batch_size=1000,
                    )
                except Exception as e:
                    logToDB(
                        f"Unable to batch update running totals: {e}",
                        None,
                        None,
                        None,
                        3001902,
                        2,
                    )
            except Exception as e:
                logToDB(
                    f"Full update of running totals error: {e}",
                    None,
                    None,
                    None,
                    3001902,
                    2,
                )
        # This is not a full update
        else:
            if transactions and len(transactions) != 0:
                for trans in transactions:
                    pass

                def get_sort_order(obj):
                    return obj.sort_order

                ordered_transactions = sorted(transactions, key=get_sort_order)
                # This is a delete
                if delete:
                    # Check if more than 1 transaction, raise exception
                    if len(ordered_transactions) == 1:
                        try:
                            bulk_source_transactions = []
                            transactions_to_update = (
                                Transaction.objects.filter(
                                    Q(
                                        source_account_id=ordered_transactions[
                                            0
                                        ].source_account_id
                                    )
                                    | Q(
                                        destination_account_id=ordered_transactions[
                                            0
                                        ].source_account_id
                                    ),
                                    sort_order__gte=ordered_transactions[
                                        0
                                    ].sort_order,
                                )
                                .exclude(id=ordered_transactions[0].id)
                                .order_by("sort_order")
                            )
                            for trans in transactions_to_update:
                                if (
                                    trans.source_account_id
                                    == ordered_transactions[0].source_account_id
                                ):
                                    trans.source_running_total -= Decimal(
                                        ordered_transactions[0].total_amount
                                    )
                                if (
                                    trans.destination_account_id
                                    == ordered_transactions[0].source_account_id
                                ):
                                    trans.destination_running_total -= Decimal(
                                        abs(
                                            ordered_transactions[0].total_amount
                                        )
                                    )
                                bulk_source_transactions.append(trans)
                            try:
                                Transaction.objects.bulk_update(
                                    bulk_source_transactions,
                                    [
                                        "source_running_total",
                                        "destination_running_total",
                                    ],
                                    batch_size=1000,
                                )
                            except Exception as e:
                                logToDB(
                                    f"Batch update of partial delete source error: {e}",
                                    None,
                                    None,
                                    None,
                                    3001902,
                                    2,
                                )
                            if ordered_transactions[0].destination_account_id:
                                bulk_destination_transactions = []
                                transactions_to_update = Transaction.objects.filter(
                                    Q(
                                        source_account_id=ordered_transactions[
                                            0
                                        ].destination_account_id
                                    )
                                    | Q(
                                        destination_account_id=ordered_transactions[
                                            0
                                        ].destination_account_id
                                    ),
                                    sort_order__gt=ordered_transactions[
                                        0
                                    ].sort_order,
                                ).order_by(
                                    "sort_order"
                                )
                                for trans in transactions_to_update:
                                    if (
                                        trans.source_account_id
                                        == ordered_transactions[
                                            0
                                        ].destination_account_id
                                    ):
                                        trans.source_running_total += Decimal(
                                            ordered_transactions[0].total_amount
                                        )
                                    if (
                                        trans.destination_account_id
                                        == ordered_transactions[
                                            0
                                        ].destination_account_id
                                    ):
                                        trans.destination_running_total += (
                                            Decimal(
                                                abs(
                                                    ordered_transactions[
                                                        0
                                                    ].total_amount
                                                )
                                            )
                                        )
                                    bulk_destination_transactions.append(trans)
                                try:
                                    Transaction.objects.bulk_update(
                                        bulk_destination_transactions,
                                        [
                                            "source_running_total",
                                            "destination_running_total",
                                        ],
                                        batch_size=1000,
                                    )
                                except Exception as e:
                                    logToDB(
                                        f"Batch update of partial delete destination error: {e}",
                                        None,
                                        None,
                                        None,
                                        3001902,
                                        2,
                                    )
                        except Exception as e:
                            logToDB(
                                f"Update of running totals after delete error: {e}",
                                None,
                                None,
                                None,
                                3001902,
                                2,
                            )
                    else:
                        raise Exception("Too many transactions for deletion")
                # This is not a delete
                else:
                    try:
                        for trans in ordered_transactions:
                            print(f"trans: {trans.source_account_id}")
                            # Update Source Account Balance
                            source_account = Account.objects.get(
                                id=trans.source_account_id
                            )
                            source_balance = Decimal(0.00)
                            source_balance += trans.total_amount
                            source_previous_transaction = (
                                Transaction.objects.filter(
                                    Q(source_account_id=trans.source_account_id)
                                    | Q(
                                        destination_account_id=trans.source_account_id
                                    ),
                                    sort_order__lt=trans.sort_order,
                                )
                                .order_by("sort_order")
                                .last()
                            )
                            if source_previous_transaction:
                                if (
                                    source_previous_transaction.source_account_id
                                    == trans.source_account_id
                                ):
                                    source_balance += Decimal(
                                        source_previous_transaction.source_running_total
                                    )
                                if (
                                    source_previous_transaction.destination_account_id
                                    == trans.source_account_id
                                ):
                                    source_balance += Decimal(
                                        source_previous_transaction.destination_running_total
                                    )
                            else:
                                source_balance += source_account.opening_balance
                            trans.source_running_total = source_balance

                            # Update Destination Account Balance
                            destination_balance = Decimal(0.00)
                            if trans.destination_account_id is not None:
                                destination_account = Account.objects.get(
                                    id=trans.destination_account_id
                                )
                                destination_balance += abs(
                                    Decimal(trans.total_amount)
                                )
                                destination_previous_transaction = (
                                    Transaction.objects.filter(
                                        Q(
                                            source_account_id=trans.destination_account_id
                                        )
                                        | Q(
                                            destination_account_id=trans.destination_account_id
                                        ),
                                        sort_order__lt=trans.sort_order,
                                    )
                                    .order_by("sort_order")
                                    .last()
                                )
                                if destination_previous_transaction:
                                    if (
                                        destination_previous_transaction.source_account_id
                                        == trans.destination_account_id
                                    ):
                                        destination_balance += Decimal(
                                            destination_previous_transaction.source_running_total
                                        )
                                    if (
                                        destination_previous_transaction.destination_account_id
                                        == trans.destination_account_id
                                    ):
                                        destination_balance += Decimal(
                                            destination_previous_transaction.destination_running_total
                                        )
                                else:
                                    destination_balance += (
                                        destination_account.opening_balance
                                    )
                            trans.destination_running_total = (
                                destination_balance
                            )

                            # Save changes to transaction
                            trans.save()

                            # Update subsequent source account transactions
                            bulk_source_transactions = []
                            transactions_to_update = Transaction.objects.filter(
                                Q(source_account_id=trans.source_account_id)
                                | Q(
                                    destination_account_id=trans.source_account_id
                                ),
                                sort_order__gt=trans.sort_order,
                            ).order_by("sort_order")
                            for sub_trans in transactions_to_update:
                                if (
                                    sub_trans.source_account_id
                                    == trans.source_account_id
                                ):
                                    source_balance += Decimal(
                                        sub_trans.total_amount
                                    )
                                    sub_trans.source_running_total = (
                                        source_balance
                                    )
                                if (
                                    sub_trans.destination_account_id
                                    == trans.source_account_id
                                ):
                                    source_balance += Decimal(
                                        abs(sub_trans.total_amount)
                                    )
                                    sub_trans.destination_running_total = (
                                        source_balance
                                    )
                                bulk_source_transactions.append(sub_trans)
                            try:
                                Transaction.objects.bulk_update(
                                    bulk_source_transactions,
                                    [
                                        "source_running_total",
                                        "destination_running_total",
                                    ],
                                    batch_size=1000,
                                )
                            except Exception as e:
                                logToDB(
                                    f"Batch update of partial source error: {e}",
                                    None,
                                    None,
                                    None,
                                    3001902,
                                    2,
                                )

                            # Update subsequent destination account transactions
                            if trans.destination_account_id:
                                bulk_destination_transactions = []
                                transactions_to_update = Transaction.objects.filter(
                                    Q(
                                        source_account_id=trans.destination_account_id
                                    )
                                    | Q(
                                        destination_account_id=trans.destination_account_id
                                    ),
                                    sort_order__gt=trans.sort_order,
                                ).order_by(
                                    "sort_order"
                                )
                                for sub_trans in transactions_to_update:
                                    if (
                                        sub_trans.source_account_id
                                        == trans.destination_account_id
                                    ):
                                        destination_balance += Decimal(
                                            sub_trans.total_amount
                                        )
                                        sub_trans.source_running_total = (
                                            destination_balance
                                        )
                                    if (
                                        sub_trans.destination_account_id
                                        == trans.destination_account_id
                                    ):
                                        destination_balance += Decimal(
                                            abs(sub_trans.total_amount)
                                        )
                                        sub_trans.destination_running_total = (
                                            destination_balance
                                        )
                                    bulk_destination_transactions.append(
                                        sub_trans
                                    )
                                try:
                                    Transaction.objects.bulk_update(
                                        bulk_destination_transactions,
                                        [
                                            "source_running_total",
                                            "destination_running_total",
                                        ],
                                        batch_size=1000,
                                    )
                                except Exception as e:
                                    logToDB(
                                        f"Batch update of partial destination error: {e}",
                                        None,
                                        None,
                                        None,
                                        3001902,
                                        2,
                                    )
                    except Exception as e:
                        logToDB(
                            f"Update of running totals error: {e}",
                            None,
                            None,
                            None,
                            3001902,
                            2,
                        )
            else:
                raise Exception("No transactions to update")
        logToDB(
            "Updated running totals successfully",
            None,
            None,
            None,
            3001002,
            1,
        )
        return True
    except Exception as e:
        logToDB(
            f"Updating running totals failed: {e}",
            None,
            None,
            None,
            3001902,
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
