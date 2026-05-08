from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand

from reminders.models import Reminder, ReminderExclusion


class Command(BaseCommand):
    help = (
        "Repairs reminders whose start_date falls on an excluded date — a side-effect "
        "of a bug where manual reminder conversion did not advance start_date. "
        "Advances start_date (and next_date) to the next non-excluded occurrence."
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

        for reminder in Reminder.objects.select_related("repeat").all():
            if not ReminderExclusion.objects.filter(
                reminder=reminder, exclude_date=reminder.start_date
            ).exists():
                skipped += 1
                continue

            # start_date is excluded — advance to the next valid date
            repeat = reminder.repeat
            candidate = reminder.start_date
            while ReminderExclusion.objects.filter(
                reminder=reminder, exclude_date=candidate
            ).exists():
                candidate += relativedelta(
                    days=repeat.days,
                    weeks=repeat.weeks,
                    months=repeat.months,
                    years=repeat.years,
                )

            self.stdout.write(
                f"Reminder {reminder.id} ({reminder.description!r}): "
                f"start_date {reminder.start_date} → {candidate}"
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
