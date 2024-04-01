"""
Module: models.py
Description: Contains django model definitions.

Author: John Adams <johnmadams96@gmail.com>
Date: February 15, 2024
"""

from django.db import models
from datetime import date
from django.utils import timezone


def import_file_name(instance, filename):
    timestamp = timezone.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"imports/import-{timestamp}.csv"


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
    """

    transaction_date = models.DateField(default=date.today)
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    status = models.ForeignKey(
        TransactionStatus, on_delete=models.SET_NULL, null=True, blank=True
    )
    memo = models.CharField(max_length=254)
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
    - message_date (DateField): The date of the message, defaults to today.
    - message (CharField): The text of the messsage, limited to 254 characters.
    - unread (BooleanField): Whether or not this message is unread, default is True.
    """

    message_date = models.DateTimeField(default=timezone.now())
    message = models.CharField(max_length=254)
    unread = models.BooleanField(default=True)

    def __str__(self):
        return self.message


class FileImport(models.Model):
    """
    Model representing a file import to import transactions.

    Fields:
    - import_file (FileField): The transcation import file.
    - mappings_file (FileField): A mapping file to map fields correctly.
    """

    import_file = models.FileField(upload_to=import_file_name)


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
    memo = models.CharField(max_length=254)
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
