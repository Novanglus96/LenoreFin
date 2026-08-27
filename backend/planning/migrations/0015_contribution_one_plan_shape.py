"""Collapse the contribution's three overlapping plans into one shape.

The model carried the same fact several times over. `emergency_amt` and
`emergency_diff` always summed to `per_paycheck` — on every row, without
exception — so the emergency plan was a second set of stored numbers rather
than a different question. `goal_type` had seven variants, several of which
said what a budget or a reminder already said.

Nothing is lost here:

- `emergency_amt` becomes `minimum_per_paycheck`. It always was the floor a
  contribution may not go below; naming it that lets normal, emergency and
  windfall planning share one field instead of three.
- `emergency_diff` is dropped because it is `per_paycheck - minimum`, derivable
  at any moment and otherwise just another thing to keep in step.
- `cap` becomes `target_balance`, which is what it was being used for.
- `goal_type == "maximise"` becomes `sweep`.

`goal_amount` is dropped rather than migrated. For every FLOOR row it held a
variance heuristic the planner suggested, not a figure anyone chose, and
treating those as obligations is what made the plan unbuildable — Car Savings'
2,932 "floor" outranked the mortgage. The caps in `cap` are real numbers a
person typed, so those survive.
"""

from django.db import migrations, models


def zero_cap_means_no_target(apps, schema_editor):
    """`cap` defaulted to 0 to mean "no cap"; `target_balance` says that as null.

    Left as 0 it would read as "accumulate to nothing", which would stop every
    uncapped bucket being funded at all.
    """
    Contribution = apps.get_model("planning", "Contribution")
    Contribution.objects.filter(target_balance=0).update(target_balance=None)


def no_target_means_zero_cap(apps, schema_editor):
    Contribution = apps.get_model("planning", "Contribution")
    Contribution.objects.filter(target_balance=None).update(target_balance=0)


def maximise_becomes_sweep(apps, schema_editor):
    Contribution = apps.get_model("planning", "Contribution")
    Contribution.objects.filter(goal_type="maximise").update(sweep=True)


def sweep_becomes_maximise(apps, schema_editor):
    Contribution = apps.get_model("planning", "Contribution")
    Contribution.objects.filter(sweep=True).update(goal_type="maximise")


class Migration(migrations.Migration):
    # Not atomic: the data migrations sit between schema changes on the same
    # table, and Postgres refuses to ALTER a table that has pending trigger
    # events from an UPDATE earlier in the same transaction.
    atomic = False

    dependencies = [("planning", "0014_contribution_budgets")]

    operations = [
        # The nullable minimum added last session is redundant with
        # `emergency_amt`, which has held exactly this for years. Drop the new
        # one so the old one can take the name and keep its data.
        migrations.RemoveField(
            model_name="contribution", name="minimum_per_paycheck"
        ),
        migrations.AddField(
            model_name="contribution",
            name="sweep",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(maximise_becomes_sweep, sweep_becomes_maximise),
        migrations.RenameField(
            model_name="contribution",
            old_name="emergency_amt",
            new_name="minimum_per_paycheck",
        ),
        migrations.RenameField(
            model_name="contribution",
            old_name="cap",
            new_name="target_balance",
        ),
        migrations.AlterField(
            model_name="contribution",
            name="minimum_per_paycheck",
            field=models.DecimalField(
                blank=True, decimal_places=2, default=None, max_digits=12, null=True
            ),
        ),
        migrations.AlterField(
            model_name="contribution",
            name="target_balance",
            field=models.DecimalField(
                blank=True, decimal_places=2, default=None, max_digits=12, null=True
            ),
        ),
        migrations.AddField(
            model_name="contribution",
            name="target_date",
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.RunPython(zero_cap_means_no_target, no_target_means_zero_cap),
        migrations.RemoveField(model_name="contribution", name="emergency_diff"),
        migrations.RemoveField(model_name="contribution", name="goal_type"),
        migrations.RemoveField(model_name="contribution", name="goal_amount"),
        migrations.RemoveField(model_name="contribution", name="goal_date"),
        migrations.RemoveField(model_name="contribution", name="goal_rate"),
    ]
