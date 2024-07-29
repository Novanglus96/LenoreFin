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
from accounts.models import Account
from reminders.models import Reminder

# Create your models here.


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk and self.__class__.objects.exists():
            raise ValidationError("There is already one instance of this model")
        return super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("You cannot delete this object")


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


class Option(SingletonModel):
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

    @classmethod
    def load(cls):
        return cls.objects.first()


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
        Reminder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    transaction = models.ForeignKey(
        "transactions.Transaction",
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
