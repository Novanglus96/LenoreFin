# A cushion a bucket holds above zero. Until now `required_rate` solved every
# bucket against a floor of 0.00, so the plan funded each one to exactly nothing
# on its worst day — solvency, not comfort. A bucket whose spending is budgeted
# rather than scheduled needs room for the budget being a little wrong.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("planning", "0020_rename_contribution_to_bucket")]

    operations = [
        migrations.AddField(
            model_name="bucket",
            name="buffer",
            field=models.DecimalField(decimal_places=2, default=0.00, max_digits=12),
        ),
    ]
