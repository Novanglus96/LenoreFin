from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    for model_name in ("TransactionType", "TransactionStatus"):
        Model = apps.get_model("transactions", model_name)
        field = "transaction_type" if model_name == "TransactionType" else "transaction_status"
        for obj in Model.objects.all():
            base = slugify(getattr(obj, field))
            slug = base
            n = 2
            while Model.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            obj.slug = slug
            obj.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0009_transaction_types_slug_is_system"),
    ]

    operations = [
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="transactionstatus",
            name="slug",
            field=models.SlugField(blank=True, max_length=120, unique=True),
        ),
        migrations.AlterField(
            model_name="transactiontype",
            name="slug",
            field=models.SlugField(blank=True, max_length=120, unique=True),
        ),
    ]
