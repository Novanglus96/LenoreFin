import pytest
from tags.models import Tag, SubTag
from django.db import IntegrityError


@pytest.mark.django_db
def test_tag_creation(test_main_tag, test_sub_tag, tag_type_expense):
    tag = Tag.objects.create(
        parent=test_main_tag, child=test_sub_tag, tag_type=tag_type_expense
    )

    assert tag.id is not None
    assert tag.parent == test_main_tag
    assert tag.child == test_sub_tag
    assert tag.tag_type == tag_type_expense


@pytest.mark.django_db
def test_tag_defaults(test_main_tag, tag_type_expense):
    tag = Tag.objects.create(parent=test_main_tag, tag_type=tag_type_expense)

    assert tag.id is not None
    assert tag.child is None


@pytest.mark.django_db
def test_tag_tag_name_with_child(test_main_tag, test_sub_tag, tag_type_expense):
    tag = Tag.objects.create(
        parent=test_main_tag, child=test_sub_tag, tag_type=tag_type_expense
    )
    expected = "Main Test \\ Sub Test"

    assert tag.id is not None
    assert tag.tag_name == expected


@pytest.mark.django_db
def test_tag_name_without_child(test_main_tag, tag_type_expense):
    tag = Tag.objects.create(parent=test_main_tag, tag_type=tag_type_expense)
    expected = "Main Test"

    assert tag.id is not None
    assert tag.tag_name == expected


@pytest.mark.django_db
def test_tag_string_representation(test_main_tag, tag_type_expense):
    tag = Tag.objects.create(parent=test_main_tag, tag_type=tag_type_expense)
    expected = "Main Test"

    assert tag.id is not None
    assert str(tag) == expected


@pytest.mark.django_db
def test_unique_parent_child_constraint(
    test_main_tag, test_sub_tag, tag_type_expense
):
    Tag.objects.create(
        parent=test_main_tag, child=test_sub_tag, tag_type=tag_type_expense
    )

    with pytest.raises(IntegrityError):
        Tag.objects.create(
            parent=test_main_tag, child=test_sub_tag, tag_type=tag_type_expense
        )


@pytest.mark.django_db
def test_unique_parent_null_child_constraint(test_main_tag, tag_type_expense):
    Tag.objects.create(parent=test_main_tag, tag_type=tag_type_expense)

    with pytest.raises(IntegrityError):
        Tag.objects.create(parent=test_main_tag, tag_type=tag_type_expense)


@pytest.mark.django_db
def test_same_parent_different_children_allowed(
    test_main_tag, tag_type_expense
):
    child1 = SubTag.objects.create(
        tag_name="Groceries", tag_type=tag_type_expense
    )
    child2 = SubTag.objects.create(tag_name="Dining", tag_type=tag_type_expense)

    Tag.objects.create(
        parent=test_main_tag, child=child1, tag_type=tag_type_expense
    )
    Tag.objects.create(
        parent=test_main_tag, child=child2, tag_type=tag_type_expense
    )

    assert Tag.objects.count() == 2
