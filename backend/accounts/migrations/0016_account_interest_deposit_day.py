from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0015_rename_last_statement_amount_account_statement_balance"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="interest_deposit_day",
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
