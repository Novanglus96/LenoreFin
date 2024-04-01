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
        current_timezone = timezone.get_current_timezone()
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)
        next_run_date_tomorrow = tomorrow.strftime("%Y-%m-%d")
        next_run_date_today = today.strftime("%Y-%m-%d")

        # Define tasks to be scheduled
        tasks = [
            {
                "task_name": "Send Message",
                "function": "api.tasks.create_message",
                "time": "03:15",
                "arguments": "'Hello World'",
                "type": "DAILY",
                "start_today": False,
                "delete": True,
            },
            {
                "task_name": "Convert Reminder Transactions",
                "function": "api.tasks.convert_reminder",
                "time": "00:01",
                "arguments": "",
                "type": "DAILY",  # DAILY, HOURLY, MINUTES
                "start_today": False,
                "delete": False,
            },
            {
                "task_name": "Update Forever Reminders",
                "function": "api.tasks.update_forever_reminders",
                "time": "00:02",
                "arguments": "",
                "type": "DAILY",  # DAILY, HOURLY, MINUTES
                "start_today": False,
                "delete": False,
            },
            {
                "task_name": "Finish Imports",
                "function": "api.tasks.finish_imports",
                "time": "14:15",
                "arguments": "",
                "type": "MINUTES",  # DAILY, HOURLY, MINUTES
                "start_today": True,
                "minutes": 15,
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
            next_run = next_run.astimezone(current_timezone)
            if task["type"] == "DAILY":
                schedule_type = Schedule.DAILY
            elif task["type"] == "HOURLY":
                schedule_type = Schedule.HOURLY
            elif task["type"] == "MINUTES":
                schedule_type = Schedule.MINUTES
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
