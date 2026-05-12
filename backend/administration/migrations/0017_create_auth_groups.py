from django.db import migrations


def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="Full Access")
    Group.objects.get_or_create(name="Readonly")


def delete_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["Full Access", "Readonly"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("administration", "0016_alter_descriptionhistory_description_pretty"),
    ]

    operations = [
        migrations.RunPython(create_groups, reverse_code=delete_groups),
    ]
