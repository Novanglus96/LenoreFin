# Generated by Django 4.2.3 on 2025-07-15 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reminders', '0003_reminderexclusion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reminder',
            name='memo',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
