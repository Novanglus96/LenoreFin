# Generated by Django 4.2.3 on 2024-08-06 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0003_option_archive_length_option_auto_archive'),
    ]

    operations = [
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_number', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
