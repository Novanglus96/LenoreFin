from django.core.management.base import BaseCommand, CommandError
from django_q.tasks import schedule
from django_q.models import Schedule
from datetime import date, timedelta
from django.shortcuts import get_object_or_404

class Command(BaseCommand):
    help = 'Adds periodic scheduled tasks'
    
    def handle(self, *args, **options):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_run_date = tomorrow.strftime("%Y-%m-%d")
        tasks = [
            {
                'task_name': 'Send Message',
                'function': 'api.tasks.create_message',
                'time': '03:15',
                'arguments': "'Hello World'"
            }
        ]
        for task in tasks:
            next_run = next_run_date + ' ' + task['time']
            existing_schedule = Schedule.objects.filter(name=task['task_name']).first()
            if existing_schedule:
                existing_schedule.delete()
            Schedule.objects.create(
                func=task['function'],
                args=task['arguments'],
                schedule_type=Schedule.DAILY,
                name=task['task_name'],
                next_run=next_run
            )
            