"""
Module: scheduletasks.py
Description: Add or modify scheduled tasks during project initialization.

Author: John Adams <johnmadams96@gmail.com>
Date: February 15, 2024
"""

from django.core.management.base import BaseCommand, CommandError
from django_q.tasks import schedule
from django_q.models import Schedule
from datetime import date, timedelta
from django.shortcuts import get_object_or_404


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
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_run_date = tomorrow.strftime("%Y-%m-%d")

        # Define tasks to be scheduled
        tasks = [
            {
                "task_name": "Send Message",
                "function": "api.tasks.create_message",
                "time": "03:15",
                "arguments": "'Hello World'",
            }
        ]

        # Schedule or modify tasks
        for task in tasks:
            next_run = next_run_date + " " + task["time"]
            existing_schedule = Schedule.objects.filter(
                name=task["task_name"]
            ).first()
            if existing_schedule:
                existing_schedule.func = task["function"]
                existing_schedule.args = task["arguments"]
                existing_schedule.next_run = next_run
                existing_schedule.save()
            else:
                Schedule.objects.create(
                    func=task["function"],
                    args=task["arguments"],
                    schedule_type=Schedule.DAILY,
                    name=task["task_name"],
                    next_run=next_run,
                )
