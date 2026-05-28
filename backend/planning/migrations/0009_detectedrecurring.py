from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("planning", "0008_note_text_to_textfield"),
        ("reminders", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DetectedRecurring",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.CharField(max_length=254)),
                ("estimated_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "repeat",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="reminders.repeat",
                    ),
                ),
                ("next_estimated_date", models.DateField()),
                ("transaction_ids", models.JSONField(default=list)),
                ("is_ignored", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
