from datetime import date

from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand

from reminders.models import Reminder, ReminderExclusion


def _next_valid_date(reminder, start):
    """Return the first date >= start that is not excluded for this reminder."""
    repeat = reminder.repeat
    step = relativedelta(
        days=repeat.days,
        weeks=repeat.weeks,
        months=repeat.months,
        years=repeat.years,
    )
    candidate = start
    today = date.today()
    while True:
        excluded = ReminderExclusion.objects.filter(
            reminder=reminder, exclude_date=candidate
        ).exists()
        if not excluded and candidate >= today:
            break
        candidate += step
    return candidate


class Command(BaseCommand):
    help = (
        "Repairs reminders whose start_date is in the past or falls on an excluded "
        "date — a side-effect of a bug where manual reminder conversion did not "
        "advance start_date. Advances start_date (and next_date) to the first "
        "future non-excluded occurrence."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be changed without saving anything.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write("DRY RUN — no changes will be saved.\n")

        fixed = 0
        skipped = 0
        today = date.today()

        for reminder in Reminder.objects.select_related("repeat").all():
            start_excluded = ReminderExclusion.objects.filter(
                reminder=reminder, exclude_date=reminder.start_date
            ).exists()
            start_in_past = reminder.start_date < today

            if not start_excluded and not start_in_past:
                skipped += 1
                continue

            candidate = _next_valid_date(reminder, reminder.start_date)

            self.stdout.write(
                f"Reminder {reminder.id} ({reminder.description!r}): "
                f"start_date {reminder.start_date} → {candidate}"
                + (" [excluded]" if start_excluded else "")
                + (" [past]" if start_in_past else "")
            )

            if not dry_run:
                reminder.start_date = candidate
                reminder.next_date = candidate
                reminder.save()

            fixed += 1

        status = "Would fix" if dry_run else "Fixed"
        self.stdout.write(
            f"\n{status} {fixed} reminder(s). {skipped} reminder(s) had no issue."
        )
