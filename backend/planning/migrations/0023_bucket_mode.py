"""Split what a bucket is *for* out of which fields happened to be set.

`target_balance` did two jobs. With no date it meant "hold this from today";
with a date, "reach this by then". Those are not variants of one intention —
holding 4,000 from today demands 1,225 a paycheck on this household's real
data, while reaching the same 4,000 by a date a year out demands a fraction of
it, and the difference was absorbing the whole remainder before any sweep saw a
cent.

**The mapping here is deliberately mechanical.** Which of the two a given
undated target really was is a question about what the household wants, and
this runs unattended against production where nobody is there to answer it. So
it preserves exactly what each bucket does today, and the plan asks the
question afterwards — see the Maintain note in `savings_plan._ambition`, which
prices the alternative rather than guessing at it.
"""

from django.db import migrations, models


def to_modes(apps, schema_editor):
    Bucket = apps.get_model("planning", "Bucket")
    for bucket in Bucket.objects.all():
        if bucket.sweep:
            bucket.mode = "maximise"
        elif bucket.target_balance is not None and bucket.target_date is not None:
            bucket.mode = "goal"
            bucket.goal_amount = bucket.target_balance
            bucket.goal_date = bucket.target_date
        elif bucket.target_balance is not None:
            bucket.mode = "maintain"
            bucket.minimum_balance = bucket.target_balance
        else:
            bucket.mode = "cover"
        bucket.save(
            update_fields=["mode", "minimum_balance", "goal_amount", "goal_date"]
        )


def to_targets(apps, schema_editor):
    Bucket = apps.get_model("planning", "Bucket")
    for bucket in Bucket.objects.all():
        bucket.sweep = bucket.mode == "maximise"
        if bucket.mode == "goal":
            bucket.target_balance = bucket.goal_amount
            bucket.target_date = bucket.goal_date
        elif bucket.mode == "maintain":
            bucket.target_balance = bucket.minimum_balance
            bucket.target_date = None
        else:
            bucket.target_balance = None
            bucket.target_date = None
        bucket.save(update_fields=["sweep", "target_balance", "target_date"])


class Migration(migrations.Migration):

    dependencies = [("planning", "0022_bucket_scope_main_tags")]

    operations = [
        migrations.AddField(
            model_name="bucket",
            name="mode",
            field=models.CharField(
                choices=[
                    ("cover", "Cover"),
                    ("maintain", "Maintain"),
                    ("goal", "Goal"),
                    ("maximise", "Maximise"),
                ],
                default="cover",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="bucket",
            name="minimum_balance",
            field=models.DecimalField(
                blank=True, decimal_places=2, default=None, max_digits=12, null=True
            ),
        ),
        migrations.AddField(
            model_name="bucket",
            name="goal_amount",
            field=models.DecimalField(
                blank=True, decimal_places=2, default=None, max_digits=12, null=True
            ),
        ),
        migrations.AddField(
            model_name="bucket",
            name="goal_date",
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.RunPython(to_modes, to_targets),
        migrations.RemoveField(model_name="bucket", name="target_balance"),
        migrations.RemoveField(model_name="bucket", name="target_date"),
        migrations.RemoveField(model_name="bucket", name="sweep"),
    ]
