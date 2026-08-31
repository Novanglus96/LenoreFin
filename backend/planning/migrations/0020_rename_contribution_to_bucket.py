# Vocabulary, not behaviour. The code had three different things called a
# "plan" — the stored row, one row's share of the answer, and the whole answer
# — which is why adding a fifth way to save read as dangerous. After this:
#
#   Bucket        one named pot of money and the standing intent behind it
#   contribution  the money itself, fed to a bucket each paycheck
#   SavingsPlan   every bucket solved together (computed, never stored)
#
# Every operation here is a rename, so no data moves and the whole thing is
# reversible. `ContribRule` becomes `WindfallRule` because that is what it has
# always been: free-text policy for money arriving outside the pay calendar,
# which no service computes on.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("reminders", "0001_initial"),
        ("tags", "0001_initial"),
        ("planning", "0019_budget_parent"),
    ]

    operations = [
        migrations.RenameModel(old_name="Contribution", new_name="Bucket"),
        migrations.RenameModel(old_name="ContribRule", new_name="WindfallRule"),
        # `contribution.contribution` was the bucket's name all along.
        migrations.RenameField(
            model_name="bucket", old_name="contribution", new_name="name"
        ),
        migrations.RenameField(
            model_name="bucket",
            old_name="per_paycheck",
            new_name="contribution_per_paycheck",
        ),
        # The tags are a claim on spending, not a source of funding, and the
        # name should not leave that open to interpretation.
        migrations.RenameField(
            model_name="bucket", old_name="tags", new_name="scope_tags"
        ),
        # 20 characters was enough for "Ellie" and not much else.
        migrations.AlterField(
            model_name="bucket",
            name="name",
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name="bucket",
            name="account",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="buckets",
                to="accounts.account",
            ),
        ),
        migrations.AlterField(
            model_name="bucket",
            name="reminder",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="buckets",
                to="reminders.reminder",
            ),
        ),
        migrations.AlterField(
            model_name="bucket",
            name="budgets",
            field=models.ManyToManyField(
                blank=True, related_name="buckets", to="planning.budget"
            ),
        ),
        migrations.AlterField(
            model_name="bucket",
            name="scope_tags",
            field=models.ManyToManyField(
                blank=True, related_name="buckets", to="tags.tag"
            ),
        ),
    ]
