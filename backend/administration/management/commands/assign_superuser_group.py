import os

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Assigns the Full Access group to the configured superuser if not already set."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        if not username:
            self.stdout.write("DJANGO_SUPERUSER_USERNAME not set — skipping.")
            return

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(f"Superuser '{username}' not found — skipping.")
            return

        group, _ = Group.objects.get_or_create(name="Full Access")
        if not user.groups.filter(name="Full Access").exists():
            user.groups.add(group)
            self.stdout.write(f"Added '{username}' to Full Access group.")
        else:
            self.stdout.write(f"'{username}' already in Full Access group.")
