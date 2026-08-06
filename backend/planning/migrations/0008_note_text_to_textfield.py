from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planning", "0007_rename_current_start_budget_next_start"),
    ]

    operations = [
        migrations.AlterField(
            model_name="note",
            name="note_text",
            field=models.TextField(),
        ),
    ]
