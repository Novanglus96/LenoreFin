from django.core.management.base import BaseCommand
from reminders.models import Reminder
from accounts.models import Account
from transactions.tasks import update_reminder_cache, update_cc_forecast_cache
from transactions.models import (
    ReminderCacheTransaction,
    ReminderCacheTransactionDetail,
    ForecastCacheTransaction,
    ForecastCacheTransactionDetail,
)
from django.db import connection
from django.core.management import call_command
from io import StringIO
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")


class Command(BaseCommand):
    help = "Load the caches"

    def handle(self, *args, **kwargs):
        # Clear Reminder Cache
        ReminderCacheTransaction.objects.all().delete()
        reset_ids_for_model("transactions", "remindercachetransaction")
        ReminderCacheTransactionDetail.objects.all().delete()
        reset_ids_for_model("transactions", "remindercachetransactiondetail")

        # Clear Forecast Cache
        ForecastCacheTransaction.objects.all().delete()
        reset_ids_for_model("transactions", "forecastcachetransaction")
        ForecastCacheTransactionDetail.objects.all().delete()
        reset_ids_for_model("transactions", "forecastcachetransactiondetail")

        # Recreate Reminder Cache for all reminders
        task_logger.info("Recreating reminder cache for all reminders")
        for reminder in Reminder.objects.all():
            task_logger.debug(f"Loading cache for Reminder ID#{reminder.id}")
            update_reminder_cache(reminder.id)

        # Recreate Forecast Cache for all CC Accounts
        task_logger.info("Recreating forecast cache for all CC accounts")
        for account in Account.objects.filter(account_type__slug='credit-card'):
            task_logger.debug(f"Loading cache for account #{account.id}")
            update_cc_forecast_cache(account.id)


def reset_ids_for_model(app_label, model_label):
    out = StringIO()
    call_command("sqlsequencereset", app_label, stdout=out)
    sql = out.getvalue()

    with connection.cursor() as cursor:
        cursor.execute(sql)
