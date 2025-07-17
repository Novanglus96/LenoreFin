# backend/app/management/commands/load_version_fixture.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
import json
from pathlib import Path


class Command(BaseCommand):
    help = "Load fixture with injected version from VERSION file"

    def handle(self, *args, **kwargs):
        version_path = (
            Path(__file__).resolve().parent.parent.parent.parent / "VERSION"
        )
        version = version_path.read_text().strip()

        fixture_path = Path("administration/fixtures/version.json")
        data = json.loads(fixture_path.read_text())

        for item in data:
            if item["model"] == "administration.Version":
                version_number = item["fields"].get("version_number")
                if version_number == "__VERSION__":
                    item["fields"]["version_number"] = version
                    self.stdout.write(f"Setting version_number to {version}")

        tmp_path = Path("administration/fixtures/_temp_app_metadata.json")
        tmp_path.write_text(json.dumps(data, indent=2))

        self.stdout.write(
            f"Injecting version {version} into fixture and loading it..."
        )
        call_command("loaddata", str(tmp_path))

        tmp_path.unlink()  # Clean up
