# Generated by Django 4.2.3 on 2024-10-24 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0010_option_report_individual_option_report_main'),
    ]

    operations = [
        migrations.AddField(
            model_name='option',
            name='christmas_accounts',
            field=models.CharField(blank=True, default=None, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='option',
            name='christmas_rewards',
            field=models.CharField(blank=True, default=None, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='option',
            name='retirement_accounts',
            field=models.CharField(blank=True, default=None, max_length=254, null=True),
        ),
    ]
