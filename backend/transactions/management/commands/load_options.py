from django.core.management.base import BaseCommand
from django.core.management import call_command
from administration.models import Option


class Command(BaseCommand):
    help = "Load the options fixture if the singleton record does not exist"

    def handle(self, *args, **kwargs):
        if not Option.objects.filter(pk=1).exists():
            self.stdout.write(self.style.NOTICE("Loading options fixture..."))
            call_command("loaddata", "administration/fixtures/options.json")
            self.stdout.write(self.style.SUCCESS("Options fixture loaded."))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Singleton record already exists. Skipping fixture load."
                )
            )
