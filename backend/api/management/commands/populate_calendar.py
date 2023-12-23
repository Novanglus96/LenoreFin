# api/management/commands/populate_calendar.py
import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate calendar with dates'

    def handle(self, *args, **options):
        start_date = timezone.now() - timedelta(days=365 * 10)
        end_date = timezone.now() + timedelta(days=365 * 40)
        date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

        data = [{'model': 'api.CalendarDate', 'pk': i, 'fields': {'datefield': date.strftime('%Y-%m-%d')}} for i, date in enumerate(date_range, start=1)]

        with open('api/fixtures/calendar_fixture.json', 'w') as fixture_file:
            json.dump(data, fixture_file)