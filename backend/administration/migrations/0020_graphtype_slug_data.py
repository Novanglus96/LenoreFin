from django.db import migrations
from django.utils.text import slugify


def populate_graphtype_slugs(apps, schema_editor):
    GraphType = apps.get_model("administration", "GraphType")
    for obj in GraphType.objects.all():
        base = slugify(obj.graph_type)
        slug = base
        n = 2
        while GraphType.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        obj.slug = slug
        obj.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("administration", "0019_graphtype_slug_is_system"),
    ]

    operations = [
        migrations.RunPython(populate_graphtype_slugs, migrations.RunPython.noop),
    ]
