from django.db import models
from django.db.models import Q

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


class MainTag(models.Model):
    """
    Model representing a tag for categorizing transaction details.

    Fields:
    - tag_name (CharField): The name of the tag, limited to 254 characters,
    and must be unique.
    - tag_type (ForeignKey): A reference to TagType model, representing the
    type of this tag.
    """

    tag_name = models.CharField(max_length=254, unique=True)
    tag_type = models.ForeignKey(
        TagType, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )

    def __str__(self):
        return self.tag_name


class SubTag(models.Model):
    """
    Model representing a tag for categorizing transaction details.

    Fields:
    - tag_name (CharField): The name of the tag, limited to 254 characters,
    and must be unique.
    - tag_type (ForeignKey): A reference to TagType model, representing the
    type of this tag.
    """

    tag_name = models.CharField(max_length=254, unique=True)
    tag_type = models.ForeignKey(
        TagType, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )

    def __str__(self):
        return self.tag_name


class Tag(models.Model):
    """
    Model representing a tag for categorizing transaction details.

    Fields:
    - parent (ForeignKey): A reference to MainTag, representing a parent tag.
    - child (ForeignKey): A reference to SubTag, representing a child tag.
    - tag_type (ForeignKey): A reference to TagType model, representing the
    type of this tag.
    """

    parent = models.ForeignKey(
        MainTag, on_delete=models.CASCADE, null=True, blank=True, default=None
    )
    child = models.ForeignKey(
        SubTag, on_delete=models.CASCADE, null=True, blank=True, default=None
    )
    tag_type = models.ForeignKey(
        TagType, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )

    def __str__(self):
        return self.tag_name

    @property
    def tag_name(self):
        if self.child:
            return f"{self.parent.tag_name} \ {self.child.tag_name}"
        return f"{self.parent.tag_name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "child"],
                name="unique_parent_child",
                # No condition here because we need to allow null values in child
            ),
            models.UniqueConstraint(
                fields=["parent"],
                name="unique_parent_with_null_child",
                condition=models.Q(child__isnull=True),
            ),
        ]
