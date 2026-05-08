from django.db import migrations
from django.utils.text import slugify


def populate_tag_slugs(apps, schema_editor):
    TagType = apps.get_model("tags", "TagType")
    MainTag = apps.get_model("tags", "MainTag")
    SubTag = apps.get_model("tags", "SubTag")
    Tag = apps.get_model("tags", "Tag")

    for Model, field in [(TagType, "tag_type"), (MainTag, "tag_name"), (SubTag, "tag_name")]:
        for obj in Model.objects.all():
            base = slugify(getattr(obj, field))
            slug = base
            n = 2
            while Model.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            obj.slug = slug
            obj.save(update_fields=["slug"])

    for tag in Tag.objects.select_related("parent", "child").all():
        parent_slug = tag.parent.slug if tag.parent else ""
        if tag.child and tag.child.slug:
            base = f"{parent_slug}--{tag.child.slug}"
        else:
            base = parent_slug
        slug = base
        n = 2
        while Tag.objects.filter(slug=slug).exclude(pk=tag.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        tag.slug = slug
        tag.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("tags", "0003_tags_slug_is_system"),
    ]

    operations = [
        migrations.RunPython(populate_tag_slugs, migrations.RunPython.noop),
    ]
