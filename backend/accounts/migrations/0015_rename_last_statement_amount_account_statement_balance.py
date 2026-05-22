from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_accounttype_slug_data'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='last_statement_amount',
            new_name='statement_balance',
        ),
    ]
