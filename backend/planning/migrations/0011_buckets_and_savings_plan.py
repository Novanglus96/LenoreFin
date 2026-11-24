"""Contributions become buckets, contribution rules become windfall rules.

One migration on purpose: the planner went through many shapes on a branch that
never shipped, and production is still at 0010. This takes prod's data straight
to the shape that ships.

- `Contribution.contribution` → `Bucket.name` (widened to 100).
- `Contribution.per_paycheck` → `Bucket.contribution_per_paycheck`.
- `Contribution.cap` was "the balance that shuts this contribution off", which
  is exactly a goal. A cap of 0 meant "no cap", so it becomes no goal.
- `emergency_amt` / `emergency_diff` are dropped; the plan's solvency check
  replaces the hand-kept emergency split.
"""

import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


def caps_to_goals(apps, schema_editor):
    Bucket = apps.get_model("planning", "Bucket")
    for bucket in Bucket.objects.all():
        cap = bucket.cap or Decimal("0")
        bucket.goal_amount = cap if cap > 0 else None
        bucket.save(update_fields=["goal_amount"])


def goals_to_caps(apps, schema_editor):
    Bucket = apps.get_model("planning", "Bucket")
    for bucket in Bucket.objects.all():
        bucket.cap = bucket.goal_amount or Decimal("0")
        bucket.save(update_fields=["cap"])


class Migration(migrations.Migration):
    dependencies = [
        ("planning", "0010_detectedrecurring_suggested_fields"),
        ("accounts", "0021_add_account_favorite"),
        ("reminders", "0006_repeat_slug_data"),
        ("transactions", "0010_transaction_types_slug_data"),
    ]

    operations = [
        # --- Contribution → Bucket ---
        migrations.RenameModel("Contribution", "Bucket"),
        migrations.RenameField("bucket", "contribution", "name"),
        migrations.AlterField(
            "bucket", "name", models.CharField(max_length=100, unique=True)
        ),
        migrations.RenameField("bucket", "per_paycheck", "contribution_per_paycheck"),
        migrations.AddField(
            "bucket",
            "goal_amount",
            models.DecimalField(
                blank=True, decimal_places=2, default=None, max_digits=12, null=True
            ),
        ),
        migrations.AddField(
            "bucket",
            "goal_date",
            models.DateField(blank=True, default=None, null=True),
        ),
        migrations.RunPython(caps_to_goals, goals_to_caps),
        migrations.RemoveField("bucket", "cap"),
        migrations.RemoveField("bucket", "emergency_amt"),
        migrations.RemoveField("bucket", "emergency_diff"),
        migrations.AddField(
            "bucket",
            "account",
            models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="buckets",
                to="accounts.account",
            ),
        ),
        migrations.AddField(
            "bucket",
            "reminder",
            models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="buckets",
                to="reminders.reminder",
            ),
        ),
        migrations.AlterModelOptions("bucket", {"ordering": ["name"]}),
        # --- ContribRule → WindfallRule ---
        migrations.RenameModel("ContribRule", "WindfallRule"),
        migrations.AddField(
            "windfallrule",
            "bucket",
            models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="windfall_rules",
                to="planning.bucket",
            ),
        ),
        migrations.AddField(
            "windfallrule",
            "cap_amount",
            models.DecimalField(
                blank=True, decimal_places=2, default=None, max_digits=12, null=True
            ),
        ),
        migrations.AlterModelOptions("windfallrule", {"ordering": ["order", "id"]}),
        # --- Plan acceptance ---
        migrations.CreateModel(
            name="PlanAcceptance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("accepted_on", models.DateField()),
                ("window_start", models.DateField()),
                ("window_end", models.DateField()),
                ("total_per_paycheck", models.DecimalField(decimal_places=2, max_digits=12)),
                ("verdict", models.CharField(default="ideal", max_length=10)),
                ("reverted_on", models.DateField(blank=True, default=None, null=True)),
                ("imported", models.BooleanField(default=False)),
                ("rules_snapshot", models.JSONField(blank=True, default=list)),
            ],
            options={"ordering": ["-accepted_on", "-id"]},
        ),
        migrations.CreateModel(
            name="AcceptedBucket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bucket_name", models.CharField(max_length=100)),
                ("action", models.CharField(choices=[("change", "Change"), ("create", "Create"), ("remove", "Remove")], default="change", max_length=10)),
                ("per_paycheck", models.DecimalField(decimal_places=2, max_digits=12)),
                ("previous_per_paycheck", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("previous_goal_amount", models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=12, null=True)),
                ("previous_goal_date", models.DateField(blank=True, default=None, null=True)),
                ("previous_active", models.BooleanField(default=True)),
                ("reminder_snapshots", models.JSONField(blank=True, default=list)),
                ("previous_reminder_id", models.IntegerField(blank=True, default=None, null=True)),
                ("acceptance", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="buckets", to="planning.planacceptance")),
                ("bucket", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="accepted", to="planning.bucket")),
                ("created_reminders", models.ManyToManyField(blank=True, related_name="+", to="reminders.reminder")),
            ],
            options={"ordering": ["id"]},
        ),
        # --- Windfalls ---
        migrations.CreateModel(
            name="WindfallApplication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("applied_on", models.DateField()),
                ("arrival_date", models.DateField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("allocated", models.DecimalField(decimal_places=2, max_digits=12)),
                ("reverted_on", models.DateField(blank=True, default=None, null=True)),
                ("source_account", models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="windfalls", to="accounts.account")),
            ],
            options={"ordering": ["-arrival_date", "-id"]},
        ),
        migrations.CreateModel(
            name="WindfallAllocation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bucket_name", models.CharField(max_length=100)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("suggested", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("application", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="allocations", to="planning.windfallapplication")),
                ("bucket", models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="windfall_allocations", to="planning.bucket")),
                ("transaction", models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="windfall_allocations", to="transactions.transaction")),
            ],
            options={"ordering": ["id"]},
        ),
    ]
