from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0019_populate_bank_logo_urls"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="is_favorite",
            field=models.BooleanField(default=False),
        ),
    ]
