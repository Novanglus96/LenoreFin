# Generated by Django 4.2.3 on 2024-08-20 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0005_descriptionhistory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='descriptionhistory',
            old_name='description',
            new_name='description_normalized',
        ),
        migrations.AddField(
            model_name='descriptionhistory',
            name='description_pretty',
            field=models.CharField(default=None, max_length=254),
        ),
    ]
