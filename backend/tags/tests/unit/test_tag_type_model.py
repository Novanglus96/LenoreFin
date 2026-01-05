import pytest
from tags.models import TagType
from django.db import IntegrityError


@pytest.mark.django_db
def test_tag_type_creation():
    tag_type = TagType.objects.create(tag_type="Test Tag Type")

    assert tag_type.id is not None
    assert tag_type.tag_type == "Test Tag Type"


@pytest.mark.django_db
def test_tag_type_uniqueness():
    TagType.objects.create(tag_type="Test Tag Type")

    with pytest.raises(IntegrityError):
        TagType.objects.create(tag_type="Test Tag Type")


@pytest.mark.django_db
def test_tag_type_string_repersentation():
    tag_type = TagType.objects.create(tag_type="Test Tag Type")
    expected = "Test Tag Type"

    assert str(tag_type) == expected
