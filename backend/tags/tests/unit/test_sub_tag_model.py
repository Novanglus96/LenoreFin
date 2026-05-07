import pytest
from tags.models import SubTag
from django.db import IntegrityError


@pytest.mark.django_db
def test_sub_tag_creation(tag_type_expense):
    sub_tag = SubTag.objects.create(
        tag_name="Sub Tag", tag_type=tag_type_expense
    )

    assert sub_tag.id is not None
    assert sub_tag.tag_name == "Sub Tag"
    assert sub_tag.tag_type == tag_type_expense


@pytest.mark.django_db
def test_sub_tag_defaults():
    sub_tag = SubTag.objects.create(tag_name="Sub Tag")

    assert sub_tag.id is not None
    assert sub_tag.tag_type is None


@pytest.mark.django_db
def test_sub_tag_string_representation():
    sub_tag = SubTag.objects.create(tag_name="Sub Tag")
    expected = "Sub Tag"

    assert str(sub_tag) == expected


@pytest.mark.django_db
def test_tag_name_uniqueness():
    SubTag.objects.create(tag_name="Sub Tag")

    with pytest.raises(IntegrityError):
        SubTag.objects.create(tag_name="Sub Tag")


@pytest.mark.django_db
def test_tag_type_foreign_key_setnull_delete(tag_type_expense):
    sub_tag = SubTag.objects.create(
        tag_name="Sub Tag", tag_type=tag_type_expense
    )

    assert sub_tag.id is not None
    assert sub_tag.tag_type is not None
    tag_type_expense.delete()
    sub_tag.refresh_from_db()
    assert sub_tag.tag_type is None
