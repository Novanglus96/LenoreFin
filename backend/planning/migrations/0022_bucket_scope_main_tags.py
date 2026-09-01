# Claim a family of spending, not a list of its members.
#
# `scope_tags` names individual tags, which is a snapshot: add a new
# subcategory and the bucket that obviously owns it silently does not claim it,
# and the spending appears in a category no bucket owns with nothing to say so.
# A main tag claims what does not exist yet.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tags", "0001_initial"),
        ("planning", "0021_bucket_buffer"),
    ]

    operations = [
        migrations.AddField(
            model_name="bucket",
            name="scope_main_tags",
            field=models.ManyToManyField(
                blank=True, related_name="buckets", to="tags.maintag"
            ),
        ),
    ]
