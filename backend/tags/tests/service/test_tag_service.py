import pytest
from tags.services import create_tag, update_tag, TagNotFound, InvalidTagData
from tags.models import MainTag, SubTag


@pytest.mark.django_db
@pytest.mark.service
def test_create_tag_creates_main_tag_when_parent_name_given(tag_type_expense):
    tag_id = create_tag(
        parent_id=None,
        parent_name="Brand New Parent",
        child_id=None,
        child_name=None,
        tag_type_id=tag_type_expense.id,
    )

    assert tag_id is not None
    assert MainTag.objects.filter(tag_name="Brand New Parent").exists()


@pytest.mark.django_db
@pytest.mark.service
def test_create_tag_reuses_existing_sub_tag(test_main_tag, tag_type_expense):
    SubTag.objects.create(tag_name="Reusable Child", tag_type=tag_type_expense)

    tag_id = create_tag(
        parent_id=test_main_tag.id,
        parent_name=None,
        child_id=None,
        child_name="Reusable Child",
        tag_type_id=tag_type_expense.id,
    )

    assert tag_id is not None
    assert SubTag.objects.filter(tag_name="Reusable Child").count() == 1


@pytest.mark.django_db
@pytest.mark.service
def test_create_tag_raises_invalid_data_without_parent(tag_type_expense):
    with pytest.raises(InvalidTagData):
        create_tag(
            parent_id=None,
            parent_name=None,
            child_id=None,
            child_name=None,
            tag_type_id=tag_type_expense.id,
        )


@pytest.mark.django_db
@pytest.mark.service
def test_update_tag_raises_for_missing_tag(tag_type_expense):
    with pytest.raises(TagNotFound):
        update_tag(
            tag_id=9999,
            parent_id=None,
            parent_name=None,
            child_id=None,
            child_name=None,
            tag_type_id=tag_type_expense.id,
        )


@pytest.mark.django_db
@pytest.mark.service
def test_update_tag_changes_parent(test_tag, tag_type_expense):
    new_parent = MainTag.objects.create(
        tag_name="Updated Parent", tag_type=tag_type_expense
    )

    update_tag(
        tag_id=test_tag.id,
        parent_id=new_parent.id,
        parent_name=None,
        child_id=None,
        child_name=None,
        tag_type_id=tag_type_expense.id,
    )

    test_tag.refresh_from_db()
    assert test_tag.parent_id == new_parent.id
