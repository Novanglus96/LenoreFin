from django.db import models
from django.utils import timezone
from tags.models import Tag
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import pytz
import os
from core.mixins import SystemObjectMixin


def current_date_time():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone)
    return today_tz


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


class GraphType(SystemObjectMixin, models.Model):
    """
    Model representing a graph type.

    Fields:
    - graph_type (CharField): The name of the graph type.
    """

    _slug_source_field = "graph_type"

    graph_type = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.graph_type


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
    - auto_archive (BooleanField): enable auto archiving of transactions
    - archive_length (IntegerField): how many full years to keep when auto-archiving is enabled,
    default is 2
    - enable_cc_bill_calculation (BooleanField): enable Credit Card bill forecast, default is True
    """

    alert_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    alert_period = models.IntegerField(default=3)
    widget1_graph_name = models.CharField(max_length=254)
    widget1_tag_id = models.IntegerField(default=None, null=True, blank=True)
    widget1_type = models.ForeignKey(
        GraphType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="widget1_options",
    )
    widget1_month = models.IntegerField(default=0)
    widget1_exclude = models.CharField(max_length=254)
    widget2_graph_name = models.CharField(max_length=254)
    widget2_tag_id = models.IntegerField(default=None, null=True, blank=True)
    widget2_type = models.ForeignKey(
        GraphType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="widget2_options",
    )
    widget2_month = models.IntegerField(default=0)
    widget2_exclude = models.CharField(max_length=254)
    widget3_graph_name = models.CharField(max_length=254)
    widget3_tag_id = models.IntegerField(default=None, null=True, blank=True)
    widget3_type = models.ForeignKey(
        GraphType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="widget3_options",
    )
    widget3_month = models.IntegerField(default=0)
    widget3_exclude = models.CharField(max_length=254)
    auto_archive = models.BooleanField(default=True)
    archive_length = models.IntegerField(default=2)
    enable_cc_bill_calculation = models.BooleanField(default=True)
    report_main = models.CharField(
        max_length=254, default=None, null=True, blank=True
    )
    report_individual = models.CharField(
        max_length=254, default=None, null=True, blank=True
    )
    retirement_accounts = models.CharField(
        max_length=254, default=None, null=True, blank=True
    )
    christmas_accounts = models.CharField(
        max_length=254, default=None, null=True, blank=True
    )
    christmas_rewards = models.CharField(
        max_length=254, default=None, null=True, blank=True
    )

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


class Message(models.Model):
    """
    Model representing a message alert for display in the app inbox.

    Fields:
    - message_date (DateTimeField): The date of the message, defaults to today.
    - message (CharField): The text of the messsage, limited to 254 characters.
    - unread (BooleanField): Whether or not this message is unread, default is True.
    """

    message_date = models.DateTimeField(default=current_date_time)
    message = models.CharField(max_length=254)
    unread = models.BooleanField(default=True)

    def __str__(self):
        return self.message


class Version(SingletonModel):
    """
    Model representing app version.

    Fields:
    - version_number (CharField): The current version of the app.
    """

    version_number = models.CharField(max_length=25)

    def __str__(self):
        return self.version_number


class BackupConfig(SingletonModel):
    FREQUENCY_CHOICES = [
        ("HOURLY", "Hourly"),
        ("DAILY", "Daily"),
        ("WEEKLY", "Weekly"),
    ]

    backup_enabled = models.BooleanField(default=True)
    frequency = models.CharField(
        max_length=10, choices=FREQUENCY_CHOICES, default="DAILY"
    )
    backup_time = models.CharField(max_length=5, default="02:00")
    copies_to_keep = models.IntegerField(default=2)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


DEFAULT_DASHBOARD_LAYOUT = [
    {"id": "graphs", "visible": True},
    {"id": "budgets", "visible": True},
    {"id": "reminders", "visible": True},
    {"id": "transactions", "visible": True},
]

DEFAULT_GRAPH_WIDGETS = [
    {"widget_id": 1, "graph_name": "Expenses", "type_id": 1, "tag_id": None, "month": 0, "exclude": "[0]"},
    {"widget_id": 2, "graph_name": "Income", "type_id": 2, "tag_id": None, "month": 0, "exclude": "[0]"},
    {"widget_id": 3, "graph_name": "Untagged", "type_id": 3, "tag_id": None, "month": 0, "exclude": "[0]"},
]


class UserDashboardConfig(models.Model):
    """
    Stores per-user dashboard widget ordering, visibility, and graph widget configs.

    Fields:
    - user (OneToOneField): The owning user.
    - layout (JSONField): Ordered list of widget configs, each with 'id' and 'visible'.
    - graph_widgets (JSONField): Per-user config for each of the 3 pie chart widgets.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="dashboard_config"
    )
    layout = models.JSONField(default=list)
    graph_widgets = models.JSONField(default=list)

    def __str__(self):
        return f"Dashboard config for {self.user.username}"


class DescriptionHistory(models.Model):
    """
    Model representing a history of transaction descriptions.

    Fields:
    - description (CharField): A unique description, limited to 254 characters.
    - tag (ForeignKey): Optional last used tag for this description.
    """

    description_normalized = models.CharField(max_length=254, unique=True)
    description_pretty = models.CharField(
        max_length=254, default=None, null=True, blank=True
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )

    class Meta:
        verbose_name_plural = "Description histories"
