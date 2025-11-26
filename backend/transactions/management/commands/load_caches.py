from django.core.management.base import BaseCommand
from reminders.models import Reminder
from transactions.tasks import update_reminder_cache
from transactions.models import (
    ReminderCacheTransaction,
    ReminderCacheTransactionDetail,
    ForecastCacheTransaction,
    ForecastCacheTransactionDetail,
)
from django.db import connection
from django.core.management import call_command
from io import StringIO


class Command(BaseCommand):
    help = "Load the caches"

    def handle(self, *args, **kwargs):
        ReminderCacheTransaction.objects.all().delete()
        reset_ids_for_model("transactions", "remindercachetransaction")
        ReminderCacheTransactionDetail.objects.all().delete()
        reset_ids_for_model("transactions", "remindercachetransactiondetail")
        ForecastCacheTransaction.objects.all().delete()
        reset_ids_for_model("transactions", "forecastcachetransaction")
        ForecastCacheTransactionDetail.objects.all().delete()
        reset_ids_for_model("transactions", "forecastcachetransactiondetail")
        for reminder in Reminder.objects.all():
            self.stdout.write(
                self.style.NOTICE(
                    f"Loading reminder cache Reminder ID:{reminder.id}..."
                )
            )
            update_reminder_cache(reminder.id)


def reset_ids_for_model(app_label, model_label):
    out = StringIO()
    call_command("sqlsequencereset", app_label, stdout=out)
    sql = out.getvalue()

    with connection.cursor() as cursor:
        cursor.execute(sql)
