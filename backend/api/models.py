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
from django.db.models import Case, When, Q
from decimal import Decimal
import datetime
from typing import List
import datetime
from django.db import IntegrityError, connection, transaction
from django.shortcuts import get_object_or_404


def import_file_name(instance, filename):
    timestamp = timezone.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"imports/import-{timestamp}.csv"


def transaction_image_name(instance, filename):
    timestamp = timezone.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"tran_images/{timestamp}-{filename}"


def mapping_file_name(instance, filename):
    timestamp = timezone.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"imports/mapping-{timestamp}.csv"


# Create your models here.


class AccountType(models.Model):
    """
    Model representing an account type for categorizing accounts.

    Fields:
    - account_type (CharField): The name of the account type, limited to 254 characters,
    and must be unique.
    - color (CharField): The color associated with accounts of this type, default is #059669.
    - icon (CharField): The icon associciated with accounts of this type, limited to 25
    characters.
    """

    account_type = models.CharField(max_length=254, unique=True)
    color = models.CharField(max_length=7, default="#059669")
    icon = models.CharField(max_length=25)

    def __str__(self):
        return self.account_type


class Bank(models.Model):
    """
    Model representing a bank to be used for accounts.

    Fields:
    - bank_name (CharField): The name of the bank, limited to 254 characters,
    and must be unique.
    """

    bank_name = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.bank_name


class Account(models.Model):
    """
    Model representing a banking account.

    Fields:
    - account_name (CharField): The name of the account, limited to 254 characters.
    - account_type (ForeignKey): A reference to the AccountType model, representing the type of the account.
    - opening_balance (DecimalField): The initial balance of the account, defaulting to 0.00.
    - apy (DecimalField): The annual percentage yield (APY) of the account, defaulting to 0.00.
    - due_date (DateField): The due date for the account, defaulting to today's date.
    - active (BooleanField): Indicates whether the account is active or not, defaulting to True.
    - open_date (DateField): The date when the account was opened, defaulting to today's date.
    - next_cycle_date (DateField): The date of the next billing cycle for the account, defaulting to today's date.
    - statement_cycle_length (IntegerField): The length of the statement cycle for the account, defaulting to 0.
    - statement_cycle_period (CharField): The period of the statement cycle, defaulting to 'd' (day).
    - rewards_amount (DecimalField): The amount of rewards associated with the account, defaulting to 0.00.
    - credit_limit (DecimalField): The credit limit of the account, defaulting to 0.00.
    - bank (ForeignKey): A reference to the Bank model representing the bank associated with the account.
    - last_statement_amount (DecimalField): The amount of the last statement for the account, defaulting to 0.00.
    """

    account_name = models.CharField(max_length=254, unique=True)
    account_type = models.ForeignKey(
        AccountType, null=True, on_delete=models.SET_NULL
    )
    opening_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=True
    )
    apy = models.DecimalField(
        max_digits=4, decimal_places=2, default=0.00, null=True
    )
    due_date = models.DateField(default=date.today, null=True)
    active = models.BooleanField(default=True)
    open_date = models.DateField(default=date.today, null=True)
    next_cycle_date = models.DateField(default=date.today, null=True)
    statement_cycle_length = models.IntegerField(default=0, null=True)
    statement_cycle_period = models.CharField(
        max_length=1, null=True, default="d"
    )
    rewards_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=True
    )
    credit_limit = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=True
    )
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    last_statement_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=True
    )

    def __str__(self):
        return self.account_name


class TagType(models.Model):
    """
    Model representing a tag type for categorizing tags.

    Fields:
    - tag_type (CharField): The type of the tag, limited to 254 characters
    and must be unique.
    """

    tag_type = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.tag_type


class Tag(models.Model):
    """
    Model representing a tag for categorizing transaction details.

    Fields:
    - tag_name (CharField): The name of the tag, limited to 254 characters,
    and must be unique.
    - parent (ForeignKey): A reference to self, representing a parent tag.
    - tag_type (ForeignKey): A reference to TagType model, representing the
    type of this tag.
    """

    tag_name = models.CharField(max_length=254, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )
    tag_type = models.ForeignKey(
        TagType, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )

    def __str__(self):
        return self.tag_name


class ChristmasGift(models.Model):
    """
    Model representing a christmas gift.

    Fields:
    - budget (DecimalField): The amount to budget to this christmas gift, default is
    0.00.
    - tag (ForeignKey): A reference to Tag model, representing the tag associated with
    this christmas gift.
    """

    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tag = models.ForeignKey(Tag, null=True, on_delete=models.SET_NULL)


class ContribRule(models.Model):
    """
    Model representing a contribution rule describing a rule for extra money each
    paycheck.

    Fields:
    - rule (CharField): The description of the contribution rule, limited to 254 characters.
    - cap (CharField): The cap rule for this contribution rule, lmited to 254 charaters.
    """

    rule = models.CharField(max_length=254, unique=True)
    cap = models.CharField(max_length=254, null=True, blank=True, default=None)

    def __str__(self):
        return self.rule


class Contribution(models.Model):
    """
    Model representing a contribution to be taken out each paycheck.

    Fields:
    - contribution (CharField): The description of the contribution, limited to 254 characters,
    and must be unique.
    - per_paycheck (DecimalField): The amount to deduct per paycheck for this contribution, default
    is 0.00.
    - emergency_amt (DecimalField): The amount that can be diverted in an emergency, per paycheck,
    defult is 0.00.
    - emergency_diff (DecimalField): The amount left in an emergency, per paycheck, default is 0.00.
    - cap (DecimalField): The cap for destination contibution that shuts off this contribution, default
    is 0.00.
    - active (BooleanField): Wether or not this contribution is active.
    """

    contribution = models.CharField(max_length=20, unique=True)
    per_paycheck = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    emergency_amt = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    emergency_diff = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    cap = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.contribution


class ErrorLevel(models.Model):
    """
    Model representing an error level for logging.

    Fields:
    - error_level (CharField): The name of the error level, limited to 25 characters,
    and must be unique.
    """

    error_level = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.error_level


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


class Repeat(models.Model):
    """
    Model representing a repeat period for reminders. Defined by setting how many
    days, weeks, months and years are in the repeat period.  Can be combined to create
    a custom repeat period.

    Fields:
    - repeat_name (CharField): The name of the repeat, limited to 254 characters,
    and must be unique.
    - days (IntegerField): The amount of days in this repeat period.
    - weeks (IntegerField): The amount of weeks in this repeat period.
    - months (IntegerField): The amount of months in this repeat period.
    - years (IntegerField): The amount of years in this repeat period.
    """

    repeat_name = models.CharField(max_length=254, unique=True)
    days = models.IntegerField(default=0)
    weeks = models.IntegerField(default=0)
    months = models.IntegerField(default=0)
    years = models.IntegerField(default=0)

    def __str__(self):
        return self.repeat_name


class Reminder(models.Model):
    """
    Model representing a reminder, which is a repeating transaction.

    Fields:
    - tag (ForeignKey): a refemrece to the Tag model, which categories the
    transaction details related to this reminder.
    - reminder_source_account (ForeignKey): a reference to the Account model,
    which represents the source account for transaction details related to this
    reminder.
    - reminder_destination_account (ForeignKey): a reference to the Account model,
    which represents the destination account for transaction details related to this
    reminder.  Can be null and is only used for transfers.
    - description (CharField): the description of transactions related to this reminder,
    limited to 254 characters.
    - transaction_type (ForeignKey): a reference to the TransactionType model, which
    represents the type of transactions related to this reminder.
    - start_date (DateField): the date reminder transactions start for this reminder,
    defaults to today.
    - next_date (DateField): the date of the next transaction associated with this reminder,
    can be null.
    - end_date (DateField): the last date of transactions associated with this reminder, can
    be null if this reminder has no end.
    - repeat (ForeignKey): a reference to the Repeat model, representing the repeat period
    that this reminder follows.
    - auto_add (BooleanField): whether the system auto adds the transactions, default is false.
    """

    tag = models.ForeignKey(
        Tag, on_delete=models.SET_NULL, null=True, blank=True
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    reminder_source_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reminder_source_account",
    )
    reminder_destination_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reminder_destination_account",
    )
    description = models.CharField(max_length=254)
    transaction_type = models.ForeignKey(
        TransactionType, on_delete=models.SET_NULL, null=True, blank=True
    )
    start_date = models.DateField(default=date.today)
    next_date = models.DateField(default=None, null=True, blank=True)
    end_date = models.DateField(default=None, null=True, blank=True)
    repeat = models.ForeignKey(
        Repeat, on_delete=models.SET_NULL, null=True, blank=True
    )
    auto_add = models.BooleanField(default=False)

    def __str__(self):
        return self.description


class Note(models.Model):
    """
    Model representing a note used to add notes relevant to planning.

    Fields:
    - note_text (CharField): The text of the note, limited to 254 characters
    - note_date (DateField): the date this note was added, defaults to today.
    """

    note_text = models.CharField(max_length=254)
    note_date = models.DateField(default=date.today)

    def __str__(self):
        return self.note_date


class Option(models.Model):
    """
    Model representing options to be used in the application.

    Fields:
    - log_level (ForeignKey): a reference to the log level model, representing
    the minimum log level for log entries.
    - alert_balance (DecimalField): the amount an account balance must go below
    to generate an alert message.
    - alert_period (IntegerField): the amount of months in the future to check for
    a low balance to create an alert message.
    - widget1_graph_name (CharField): The name of the graph, limited to 254
    characters.
    - widget1_tag_id (IntegerField): The tag id of the parent tag of sub tags to
    display data for in this graph.  Optional.
    - widget1_expense (BooleanField): If no tag is specified, show the graph for expenses
    or income.  Default is expenses.
    - widget1_month (IntegerField): which month to show data from, with 0 being this month.
    Default is 0.
    - widget1_exclude (CharField): a list of tag ids to exclude from the graph.  Optional
    Default is blank.
    - widget2_graph_name (CharField): The name of the graph, limited to 254
    characters.
    - widget2_tag_id (IntegerField): The tag id of the parent tag of sub tags to
    display data for in this graph.  Optional.
    - widget2_expense (BooleanField): If no tag is specified, show the graph for expenses
    or income.  Default is expenses.
    - widget2_month (IntegerField): which month to show data from, with 0 being this month.
    Default is 0.
    - widget2_exclude (CharField): a list of tag ids to exclude from the graph.  Optional
    Default is blank.
    - widget3_graph_name (CharField): The name of the graph, limited to 254
    characters.
    - widget3_tag_id (IntegerField): The tag id of the parent tag of sub tags to
    display data for in this graph.  Optional.
    - widget3_expense (BooleanField): If no tag is specified, show the graph for expenses
    or income.  Default is expenses.
    - widget3_month (IntegerField): which month to show data from, with 0 being this month.
    Default is 0.
    - widget3_exclude (CharField): a list of tag ids to exclude from the graph.  Optional
    Default is blank.
    """

    log_level = models.ForeignKey(
        ErrorLevel, on_delete=models.SET_NULL, null=True, blank=True
    )
    alert_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    alert_period = models.IntegerField(default=3)
    widget1_graph_name = models.CharField(max_length=254)
    widget1_tag_id = models.IntegerField(default=None, null=True, blank=True)
    widget1_expense = models.BooleanField(default=True)
    widget1_month = models.IntegerField(default=0)
    widget1_exclude = models.CharField(max_length=254)
    widget2_graph_name = models.CharField(max_length=254)
    widget2_tag_id = models.IntegerField(default=None, null=True, blank=True)
    widget2_expense = models.BooleanField(default=True)
    widget2_month = models.IntegerField(default=0)
    widget2_exclude = models.CharField(max_length=254)
    widget3_graph_name = models.CharField(max_length=254)
    widget3_tag_id = models.IntegerField(default=None, null=True, blank=True)
    widget3_expense = models.BooleanField(default=True)
    widget3_month = models.IntegerField(default=0)
    widget3_exclude = models.CharField(max_length=254)


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


class Payee(models.Model):
    """
    Model representing a payee for paychecks.

    Fields:
    - payee_name (CharField): The name of the payee, limited to 254 characters,
    must be unique.
    """

    payee_name = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.payee_name


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
        Payee, on_delete=models.SET_NULL, null=True, blank=True, default=None
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
    - reminder (ForeignKey): A reference to the Reminder model, representing a reminder
    associated with this transaction.  Default is None, and is Optional.
    - paycheck (ForeignKey): A reference to the Paycheck model, representing a paycheck
    associated with this transaction.  Default is None, and is Optional.
    - checkNumber (IntegerField): Number of a check associated with this transaction. Default
    is None, and is Optional.
    - source_running_total (DecimalField): Running total as seen from source account.
    - destination_running_total (DecimalField): Running total as seen from the destination account.
    """

    transaction_date = models.DateField(default=date.today)
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    status = models.ForeignKey(
        TransactionStatus, on_delete=models.SET_NULL, null=True, blank=True
    )
    memo = models.CharField(max_length=508, null=True, blank=True, default=None)
    description = models.CharField(max_length=254)
    edit_date = models.DateField(default=date.today)
    add_date = models.DateField(default=date.today)
    transaction_type = models.ForeignKey(
        TransactionType, on_delete=models.SET_NULL, null=True, blank=True
    )
    reminder = models.ForeignKey(
        Reminder, on_delete=models.CASCADE, null=True, blank=True, default=None
    )
    paycheck = models.ForeignKey(
        Paycheck, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    checkNumber = models.IntegerField(null=True, blank=True, default=None)
    running_total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    sort_order = models.IntegerField(null=True, blank=True, default=None)
    account_id = models.IntegerField(default=0)
    source_account_id = models.IntegerField(null=True, blank=True, default=None)
    destination_account_id = models.IntegerField(
        null=True, blank=True, default=None
    )
    related_transaction = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name="related_transaction_reverse",
    )


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
    the parent transaction associated with this transaction detail.
    - account (ForeignKey): A refernce to the Account model, representing the
    account associated with this transaction detail.
    detail_amt (DecimalField): The amount associated with this transaction detail,
    default is 0.00.
    tag (ForeignKey): A refernce to the Tag model, representing the tag category
    ot this transaction detail.
    """

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    detail_amt = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.SET_NULL, null=True, blank=True
    )


class LogEntry(models.Model):
    """
    Model representing a log entry.

    Fields:
    - log_date (DateField): The date of the log entry, default is today.
    - log_entry (CharField): The log entry, limited to 254 characters.
    - account (ForeignKey): A reference to the Account model, representing
    the associated account with this log entry. Optional.
    - reminder (ForeignKey): A reference to the Reminder model, representing
    the associated reminder with this log entry. Optional.
    - transaction (ForeignKey): A reference to the Transaction model, representing
    the associated transaction with this log entry. Optional.
    - error_num (IntegerField): An error number associated with this log entry.
    - error_level (ForeignKey): A reference to the ErrorLevel model, representing
    the error level of this log entry.
    """

    log_date = models.DateTimeField(auto_now_add=True)
    log_entry = models.CharField(max_length=254)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True, blank=True, default=None
    )
    reminder = models.ForeignKey(
        Reminder, on_delete=models.CASCADE, null=True, blank=True, default=None
    )
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    error_num = models.IntegerField(default=None, null=True, blank=True)
    error_level = models.ForeignKey(
        ErrorLevel, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "Log entries"

    def __str__(self):
        return self.log_entry


class Message(models.Model):
    """
    Model representing a message alert for display in the app inbox.

    Fields:
    - message_date (DateTimeField): The date of the message, defaults to today.
    - message (CharField): The text of the messsage, limited to 254 characters.
    - unread (BooleanField): Whether or not this message is unread, default is True.
    """

    message_date = models.DateTimeField(default=timezone.now)
    message = models.CharField(max_length=254)
    unread = models.BooleanField(default=True)

    def __str__(self):
        return self.message


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
    memo = models.CharField(max_length=508)
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


@receiver(post_save, sender=Transaction)
def update_related_transactions(sender, instance, created, **kwargs):
    """
    Signal receiver function to update related transactions when a Transaction is saved.
    """
    # Check if the saved transaction is a transfer
    if instance.transaction_type.id == 3:
        # Get the related transaction
        if instance.related_transaction:
            related_transaction = Transaction.objects.get(
                id=instance.related_transaction.id
            )
        # Update the related transaction based on the changes in the current transaction


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
                update_sort_order(False, True, obj_list)
            else:
                update_sort_order(False, False, obj_list)
        except Exception as e:
            print(f"Failed to update sort order: {e}")
            updating_running_totals = False
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
            if created_transactions and len(created_transactions) < 1000:
                update_sort_order(False, False, created_transactions)
            else:
                update_sort_order(True, False, None)
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


def update_sort_order(
    full: bool = True,
    delete: bool = False,
    transactions: List[Transaction] = [],
):
    """
    The function `update_sort_order` updates the sort order.

    Args:
        full (bool): Perform a full (all objects) sort order update
        delete (bool): Is this update a result of a deletion
        transactions (List[Transaction]): A list of transactions to update
    Returns:
        bool: Returns True or False depending on results
    """
    try:
        # Perform a full update
        if full or len(transactions) >= 1:
            try:
                status_table = TransactionStatus._meta.db_table
                table_name = Transaction._meta.db_table

                # Define the raw SQL query
                query = f"""
                WITH ordered_rows AS (
                    SELECT t.id, ROW_NUMBER() OVER (
                        ORDER BY
                            CASE WHEN status_id = 1 THEN 2
                                WHEN status_id = 2 THEN 0
                                WHEN status_id = 3 THEN 0
                                ELSE 1
                            END,
                            transaction_date,
                            total_amount DESC,
                            t.id
                    ) as row_num
                    FROM {table_name} t
                    JOIN {status_table} s ON t.status_id = s.id
                )
                UPDATE {table_name}
                SET sort_order = ordered_rows.row_num
                FROM ordered_rows
                WHERE {table_name}.id = ordered_rows.id
                """

                # Execute the raw SQL query
                with connection.cursor() as cursor:
                    cursor.execute(query)
            except Exception as e:
                logToDB(
                    f"Full update of sort order error: {e}",
                    None,
                    None,
                    None,
                    3001902,
                    2,
                )
        # Perform a partial update
        else:
            if transactions and len(transactions) != 0:

                def get_sort_order(obj):
                    return obj.sort_order

                ordered_transactions = sorted(transactions, key=get_sort_order)
                # Update sort order after a deletion
                if delete:
                    try:
                        for trans in ordered_transactions:
                            transactions_to_update = []
                            filtered_transactions = Transaction.objects.filter(
                                sort_order__gte=trans.sort_order
                            ).exclude(id=trans.id)
                            for obj in filtered_transactions:
                                obj.sort_order -= 1
                                transactions_to_update.append(obj)
                            Transaction.objects.bulk_update(
                                transactions_to_update,
                                ["sort_order"],
                                batch_size=1000,
                            )
                    except Exception as e:
                        logToDB(
                            f"Sort order after deletion error: {e}",
                            None,
                            None,
                            None,
                            3001902,
                            2,
                        )
                else:
                    # This is not a deletion
                    try:
                        for trans in ordered_transactions:
                            all_transactions = Transaction.objects.exclude(
                                id=trans.id
                            )
                            pending_transactions = all_transactions.filter(
                                status__id=1
                            ).order_by("sort_order")
                            cleared_transactions = all_transactions.filter(
                                status__id__gt=1
                            ).order_by("sort_order")
                            pending_count = pending_transactions.count()
                            cleared_count = cleared_transactions.count()
                            greater_transactions = None
                            lesser_transactions = None
                            same_transactions = None
                            new_sort_order = 1
                            if trans.status_id == 1:
                                new_sort_order += cleared_count
                                greater_transactions = pending_transactions.filter(
                                    transaction_date__gt=trans.transaction_date
                                )
                                lesser_transactions = pending_transactions.filter(
                                    transaction_date__lt=trans.transaction_date
                                )
                                same_transactions = pending_transactions.filter(
                                    transaction_date=trans.transaction_date
                                )
                            else:
                                greater_transactions = cleared_transactions.filter(
                                    transaction_date__gt=trans.transaction_date
                                )
                                lesser_transactions = cleared_transactions.filter(
                                    transaction_date__lt=trans.transaction_date
                                )
                                same_transactions = cleared_transactions.filter(
                                    transaction_date=trans.transaction_date
                                )
                            if same_transactions.count() > 0:
                                if (
                                    same_transactions.last().total_amount
                                    > trans.total_amount
                                ):
                                    new_sort_order = (
                                        same_transactions.last().sort_order + 1
                                    )
                                elif (
                                    same_transactions.first().total_amount
                                    < trans.total_amount
                                ):
                                    new_sort_order = (
                                        same_transactions.first().sort_order
                                    )
                                else:
                                    for same_trans in same_transactions:
                                        if (
                                            same_trans.total_amount
                                            < trans.total_amount
                                        ):
                                            new_sort_order = (
                                                same_trans.sort_order
                                            )
                                            break
                                        else:
                                            if (
                                                same_trans.total_amount
                                                == trans.total_amount
                                            ):
                                                new_sort_order = (
                                                    same_trans.sort_order
                                                )
                                                if same_trans.id > trans.id:
                                                    new_sort_order = (
                                                        same_trans.sort_order
                                                    )
                                                    break
                                                else:
                                                    new_sort_order += 1
                            else:
                                if lesser_transactions.count() > 0:
                                    new_sort_order = (
                                        lesser_transactions.last().sort_order
                                    )
                                else:
                                    if greater_transactions.count() > 0:
                                        new_sort_order = (
                                            greater_transactions.first().sort_order
                                        )
                            trans.sort_order = new_sort_order
                            transactions_to_update.append(trans)
                            sub_transactions = (
                                all_transactions.filter(
                                    sort_order__gte=new_sort_order
                                )
                                .exclude(id=trans.id)
                                .order_by("sort_order")
                            )
                            for sub_trans in sub_transactions:
                                sub_trans.sort_order += 1
                                transactions_to_update.append(sub_trans)
                            Transaction.objects.bulk_update(
                                transactions_to_update,
                                ["sort_order"],
                                batch_size=1000,
                            )
                    except Exception as e:
                        logToDB(
                            f"Updating sort order error: {e}",
                            None,
                            None,
                            None,
                            3001902,
                            2,
                        )
                    pass
            else:
                raise Exception("No transactions to update")
        logToDB(
            "Updated sort order successfully",
            None,
            None,
            None,
            3001002,
            1,
        )
        return True
    except Exception as e:
        logToDB(
            f"Updating sort order failed: {e}",
            None,
            None,
            None,
            3001902,
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
                balances = []
                accounts = Account.objects.all().order_by("id")
                for account in accounts:
                    bal_obj = {
                        "id": account.id,
                        "balance": account.opening_balance,
                    }
                    balances.append(bal_obj)
                transactions = Transaction.objects.all().order_by("sort_order")
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


def logToDB(message, account, reminder, trans, error, level):
    """
    The function `logToDB` creates log entries, but only if the current logging level
    set in options is lower than the specified error level.

    Args:
        message (str): The log entry message.
        account (Account): Optional, the account associated with this entry.
        reminder (Reminder): Optional, the reminder associated with this entry.
        trans (Transaction): Optional, the transactions associated with this entry.
        error (int): Optional, any error number associated with this entry.
        level (ErrorLevel): The error level of this entry.

    Returns:
        success (int): Returns the id of the created log entry.
    """

    options = get_object_or_404(Option, id=1)
    if options.log_level.id <= level:
        log_entry = LogEntry.objects.create(
            log_entry=message,
            account_id=account,
            reminder_id=reminder,
            transaction_id=trans,
            error_num=error,
            error_level_id=level,
        )
        return_id = log_entry.id
    else:
        return_id = 0
    return {"success": return_id}
