# Generated by Django 4.2.3 on 2025-07-15 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_transactiondetail_full_toggle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='memo',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
