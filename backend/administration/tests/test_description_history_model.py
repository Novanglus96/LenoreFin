import pytest
from administration.models import DescriptionHistory


@pytest.mark.django_db
def test_create_description_history(test_tag):
    description_history = DescriptionHistory.objects.create(
        description_normalized="description",
        description_pretty="Description",
        tag=test_tag,
    )

    assert description_history.description_normalized == "description"
    assert description_history.description_pretty == "Description"
    assert description_history.tag == test_tag


@pytest.mark.django_db
def test_description_history_defaults():
    description_history = DescriptionHistory.objects.create(
        description_normalized="description"
    )

    assert description_history.description_pretty is None
    assert description_history.tag is None


@pytest.mark.django_db
def test_foreign_key_setnull_tag(test_tag):
    description_history = DescriptionHistory.objects.create(
        description_normalized="description",
        description_pretty="Description",
        tag=test_tag,
    )

    assert DescriptionHistory.objects.count() == 1
    assert description_history.tag == test_tag
    test_tag.delete()
    description_history.refresh_from_db()
    assert description_history.tag is None
