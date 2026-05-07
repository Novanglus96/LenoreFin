import pytest
from planning.models import ChristmasGift


@pytest.mark.django_db
def test_christmas_gift_creation(test_tag):
    christmas_gift = ChristmasGift.objects.create(budget=1.00, tag=test_tag)

    assert christmas_gift.id is not None
    assert christmas_gift.budget == 1.00
    assert christmas_gift.tag == test_tag


@pytest.mark.django_db
def test_chrismas_gift_defaults(test_tag):
    christmas_gift = ChristmasGift.objects.create(tag=test_tag)

    assert christmas_gift.id is not None
    assert christmas_gift.budget == 0.00


@pytest.mark.django_db
def test_tag_foregin_key_setnull_delete(test_tag):
    christmas_gift = ChristmasGift.objects.create(tag=test_tag)

    assert ChristmasGift.objects.count() == 1
    test_tag.delete()
    christmas_gift.refresh_from_db()
    assert christmas_gift.tag is None
