from django.core.management.base import BaseCommand
from administration.models import BackupConfig
import logging

task_logger = logging.getLogger("task")


class Command(BaseCommand):
    help = "Create the default BackupConfig singleton if it does not exist"

    def handle(self, *args, **kwargs):
        if not BackupConfig.objects.filter(pk=1).exists():
            task_logger.info("Creating default BackupConfig")
            BackupConfig.objects.create(
                pk=1,
                backup_enabled=True,
                frequency="DAILY",
                backup_time="02:00",
                copies_to_keep=2,
            )
            task_logger.info("Default BackupConfig created.")
        else:
            task_logger.warning(
                "BackupConfig already exists. Skipping."
            )
