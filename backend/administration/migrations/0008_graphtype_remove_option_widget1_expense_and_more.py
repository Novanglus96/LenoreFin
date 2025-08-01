# Generated by Django 4.2.3 on 2024-08-22 15:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0007_alter_descriptionhistory_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='GraphType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('graph_type', models.CharField(max_length=25, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='option',
            name='widget1_expense',
        ),
        migrations.RemoveField(
            model_name='option',
            name='widget2_expense',
        ),
        migrations.RemoveField(
            model_name='option',
            name='widget3_expense',
        ),
        migrations.AddField(
            model_name='option',
            name='widget1_type',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='widget1_options', to='administration.graphtype'),
        ),
        migrations.AddField(
            model_name='option',
            name='widget2_type',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='widget2_options', to='administration.graphtype'),
        ),
        migrations.AddField(
            model_name='option',
            name='widget3_type',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='widget3_options', to='administration.graphtype'),
        ),
    ]
