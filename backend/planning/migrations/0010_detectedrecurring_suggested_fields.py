from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planning", "0009_detectedrecurring"),
    ]

    operations = [
        migrations.AddField(
            model_name="detectedrecurring",
            name="suggested_tag_id",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="detectedrecurring",
            name="suggested_account_id",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
