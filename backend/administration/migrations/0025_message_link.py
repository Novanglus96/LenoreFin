from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("administration", "0024_message_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="link",
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
    ]
