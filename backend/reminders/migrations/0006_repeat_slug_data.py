from django.db import migrations
from django.utils.text import slugify


def populate_repeat_slugs(apps, schema_editor):
    Repeat = apps.get_model("reminders", "Repeat")
    for obj in Repeat.objects.all():
        base = slugify(obj.repeat_name)
        slug = base
        n = 2
        while Repeat.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        obj.slug = slug
        obj.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("reminders", "0005_repeat_slug_is_system"),
    ]

    operations = [
        migrations.RunPython(populate_repeat_slugs, migrations.RunPython.noop),
    ]
