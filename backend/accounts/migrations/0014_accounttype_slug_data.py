from django.db import migrations
from django.utils.text import slugify


def populate_accounttype_slugs(apps, schema_editor):
    AccountType = apps.get_model("accounts", "AccountType")
    for obj in AccountType.objects.all():
        base = slugify(obj.account_type)
        slug = base
        n = 2
        while AccountType.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        obj.slug = slug
        obj.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0013_accounttype_slug_is_system"),
    ]

    operations = [
        migrations.RunPython(populate_accounttype_slugs, migrations.RunPython.noop),
    ]
