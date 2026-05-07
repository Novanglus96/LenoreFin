from django.core.management.base import BaseCommand
from django.core.management import call_command
from administration.models import Option
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")


class Command(BaseCommand):
    help = "Load the options fixture if the singleton record does not exist"

    def handle(self, *args, **kwargs):
        if not Option.objects.filter(pk=1).exists():
            task_logger.info("Loading options fixture")
            call_command("loaddata", "administration/fixtures/options.json")
            task_logger.info("Options fixture loaded.")
        else:
            task_logger.warning(
                "Singleton record already exists. Skipping fixture load."
            )
