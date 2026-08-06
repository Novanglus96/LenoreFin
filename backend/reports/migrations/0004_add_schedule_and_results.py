from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0003_add_is_shared_to_reportconfig"),
    ]

    operations = [
        migrations.AddField(
            model_name="reportconfig",
            name="is_scheduled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="reportconfig",
            name="schedule_frequency",
            field=models.CharField(
                blank=True,
                choices=[("DAILY", "Daily"), ("WEEKLY", "Weekly"), ("MONTHLY", "Monthly")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="reportconfig",
            name="schedule_day",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="reportconfig",
            name="next_run_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="ReportResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "config",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="results",
                        to="reports.reportconfig",
                    ),
                ),
                ("run_at", models.DateTimeField(auto_now_add=True)),
                ("result_data", models.JSONField(default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[("success", "Success"), ("error", "Error")],
                        default="success",
                        max_length=10,
                    ),
                ),
                ("error_message", models.TextField(blank=True, default="")),
            ],
            options={
                "ordering": ["-run_at"],
            },
        ),
    ]
