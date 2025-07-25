"""
Module: scheduletasks.py
Description: Add or modify scheduled tasks during project initialization.

Author: John Adams <johnmadams96@gmail.com>
Date: February 15, 2024
"""

from django.core.management.base import BaseCommand, CommandError
from django_q.tasks import schedule
from django_q.models import Schedule
from datetime import date, timedelta, datetime
from django.shortcuts import get_object_or_404
from django.utils import timezone
import pytz
import os


class Command(BaseCommand):
    help = "Adds or modifies periodic scheduled tasks."

    def handle(self, *args, **options):
        """
        The function `handle` adds a scheduled task to Django Q atams96@gmail.com>
        build.  If a task schedule exists, it modifies the existing.

        Args:
            self: The class instance.
            *args: Additional positional arguments.
            **options: Additional keyword arguments.
        """

        # Calculate the next run date for scheduled tasks
        today_utc = timezone.now()
        tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
        today = today_utc.astimezone(tz_timezone).date()
        current_timezone = timezone.get_current_timezone()
        tomorrow = today + timedelta(days=1)
        next_run_date_tomorrow = tomorrow.strftime("%Y-%m-%d")
        next_run_date_today = today.strftime("%Y-%m-%d")

        # Define tasks to be scheduled
        tasks = [
            {
                "task_name": "Send Message",
                "function": "transactions.tasks.create_message",
                "time": "03:15",
                "arguments": "'Hello World'",
                "type": "DAILY",
                "start_today": False,
                "delete": True,
            },
            {
                "task_name": "Convert Reminder Transactions",
                "function": "transactions.tasks.convert_reminder",
                "time": "00:01",
                "arguments": "",
                "type": "DAILY",  # DAILY, HOURLY, MINUTES
                "start_today": False,
                "delete": False,
            },
            {
                "task_name": "Update Forever Reminders",
                "function": "transactions.tasks.update_forever_reminders",
                "time": "00:02",
                "arguments": "",
                "type": "DAILY",  # DAILY, HOURLY, MINUTES
                "start_today": False,
                "delete": True,
            },
            {
                "task_name": "Archive Transactions",
                "function": "transactions.tasks.archive_transactions",
                "time": "00:02",
                "arguments": "",
                "type": "DAILY",  # DAILY, HOURLY, MINUTES
                "start_today": False,
                "delete": False,
            },
            {
                "task_name": "Finish Imports",
                "function": "transactions.tasks.finish_imports",
                "time": "15:35",
                "arguments": "",
                "type": "MINUTES",  # DAILY, HOURLY, MINUTES
                "start_today": True,
                "minutes": 5,
                "delete": False,
            },
            {
                "task_name": "Backup Database",
                "function": "transactions.tasks.create_backup",
                "time": "00:00",
                "arguments": "True,0",
                "type": "HOURLY",  # DAILY, HOURLY, MINUTES
                "start_today": True,
                "delete": False,
            },
            {
                "task_name": "Roll Over Budgets",
                "function": "transactions.tasks.roll_over_budgets",
                "time": "00:00",
                "arguments": "",
                "type": "DAILY",  # DAILY, HOURLY, MINUTES
                "start_today": True,
                "delete": False,
            },
        ]

        # Schedule or modify tasks
        for task in tasks:
            next_run = ""
            schedule_type = ""
            if task["start_today"]:
                next_run = datetime.combine(
                    today, datetime.strptime(task["time"], "%H:%M").time()
                )
            else:
                next_run = datetime.combine(
                    tomorrow, datetime.strptime(task["time"], "%H:%M").time()
                )
            next_run = tz_timezone.localize(next_run)
            next_run = next_run.astimezone(current_timezone)
            if task["type"] == "DAILY":
                schedule_type = Schedule.DAILY
            elif task["type"] == "HOURLY":
                schedule_type = Schedule.HOURLY
            elif task["type"] == "MINUTES":
                schedule_type = Schedule.MINUTES
                next_run = timezone.now()
            existing_schedule = Schedule.objects.filter(
                name=task["task_name"]
            ).first()
            if existing_schedule:
                if task["delete"]:
                    existing_schedule.delete()
                else:
                    existing_schedule.func = task["function"]
                    existing_schedule.args = task["arguments"]
                    existing_schedule.next_run = next_run
                    existing_schedule.schedule_type = schedule_type
                    if task["type"] == "MINUTES":
                        existing_schedule.minutes = task["minutes"]
                    existing_schedule.save()
            else:
                if not task["delete"]:
                    if task["type"] != "MINUTES":
                        Schedule.objects.create(
                            func=task["function"],
                            args=task["arguments"],
                            schedule_type=schedule_type,
                            name=task["task_name"],
                            next_run=next_run,
                        )
                    else:
                        Schedule.objects.create(
                            func=task["function"],
                            args=task["arguments"],
                            schedule_type=schedule_type,
                            name=task["task_name"],
                            next_run=next_run,
                            minutes=task["minutes"],
                        )
