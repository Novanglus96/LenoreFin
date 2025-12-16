import pytest
from tags.models import MainTag
from django.db import IntegrityError


@pytest.mark.django_db
def test_main_tag_creation(tag_type_expense):
    main_tag = MainTag.objects.create(
        tag_name="Main Tag", tag_type=tag_type_expense
    )

    assert main_tag.id is not None
    assert main_tag.tag_name == "Main Tag"
    assert main_tag.tag_type == tag_type_expense


@pytest.mark.django_db
def test_main_tag_defaults():
    main_tag = MainTag.objects.create(tag_name="Main Tag")

    assert main_tag.id is not None
    assert main_tag.tag_type is None


@pytest.mark.django_db
def test_main_tag_string_representation():
    main_tag = MainTag.objects.create(tag_name="Main Tag")
    expected = "Main Tag"

    assert str(main_tag) == expected


@pytest.mark.django_db
def test_tag_name_uniqueness():
    MainTag.objects.create(tag_name="Main Tag")

    with pytest.raises(IntegrityError):
        MainTag.objects.create(tag_name="Main Tag")


@pytest.mark.django_db
def test_tag_type_foreign_key_setnull_delete(tag_type_expense):
    main_tag = MainTag.objects.create(
        tag_name="Main Tag", tag_type=tag_type_expense
    )

    assert main_tag.id is not None
    assert main_tag.tag_type is not None
    tag_type_expense.delete()
    main_tag.refresh_from_db()
    assert main_tag.tag_type is None
