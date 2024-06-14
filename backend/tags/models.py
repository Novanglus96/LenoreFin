from django.db import models

# Create your models here.


class TagType(models.Model):
    """
    Model representing a tag type for categorizing tags.

    Fields:
    - tag_type (CharField): The type of the tag, limited to 254 characters
    and must be unique.
    """

    tag_type = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.tag_type


class Tag(models.Model):
    """
    Model representing a tag for categorizing transaction details.

    Fields:
    - tag_name (CharField): The name of the tag, limited to 254 characters,
    and must be unique.
    - parent (ForeignKey): A reference to self, representing a parent tag.
    - tag_type (ForeignKey): A reference to TagType model, representing the
    type of this tag.
    """

    tag_name = models.CharField(max_length=254, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )
    tag_type = models.ForeignKey(
        TagType, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )

    def __str__(self):
        return self.tag_name
