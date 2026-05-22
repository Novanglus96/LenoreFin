from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("administration", "0020_graphtype_slug_data"),
    ]

    operations = [
        migrations.CreateModel(
            name="BackupConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("backup_enabled", models.BooleanField(default=True)),
                (
                    "frequency",
                    models.CharField(
                        choices=[
                            ("HOURLY", "Hourly"),
                            ("DAILY", "Daily"),
                            ("WEEKLY", "Weekly"),
                        ],
                        default="DAILY",
                        max_length=10,
                    ),
                ),
                ("backup_time", models.CharField(default="02:00", max_length=5)),
                ("copies_to_keep", models.IntegerField(default=2)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
