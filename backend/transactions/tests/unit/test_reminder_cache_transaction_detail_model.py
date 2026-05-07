import pytest
from transactions.models import ReminderCacheTransactionDetail


@pytest.mark.django_db
def test_reminder_cache_transaction_detail_creation(
    test_reminder_transaction, test_tag
):
    reminder_cache_transaction_detail = (
        ReminderCacheTransactionDetail.objects.create(
            transaction=test_reminder_transaction,
            detail_amt=1.00,
            tag=test_tag,
            full_toggle=False,
        )
    )

    assert reminder_cache_transaction_detail.id is not None
    assert (
        reminder_cache_transaction_detail.transaction
        == test_reminder_transaction
    )
    assert reminder_cache_transaction_detail.detail_amt == 1.00
    assert reminder_cache_transaction_detail.tag == test_tag
    assert not reminder_cache_transaction_detail.full_toggle


@pytest.mark.django_db
def test_reminder_cache_transaction_detail_defaults(
    test_reminder_transaction, test_tag
):
    reminder_cache_transaction_detail = (
        ReminderCacheTransactionDetail.objects.create(
            transaction=test_reminder_transaction,
            tag=test_tag,
        )
    )

    assert reminder_cache_transaction_detail.id is not None
    assert reminder_cache_transaction_detail.detail_amt == 0.00
    assert not reminder_cache_transaction_detail.full_toggle


@pytest.mark.django_db
def test_reminder_transaction_foreign_key_cascade_delete(
    test_tag, test_reminder_transaction
):
    ReminderCacheTransactionDetail.objects.create(
        transaction=test_reminder_transaction,
        detail_amt=1.00,
        tag=test_tag,
        full_toggle=False,
    )

    assert ReminderCacheTransactionDetail.objects.count() == 1
    test_reminder_transaction.delete()
    assert ReminderCacheTransactionDetail.objects.count() == 0


@pytest.mark.django_db
def test_tag_foreign_key_set_null_delete(test_tag, test_reminder_transaction):
    reminder_cache_transaction_detail = (
        ReminderCacheTransactionDetail.objects.create(
            transaction=test_reminder_transaction,
            detail_amt=1.00,
            tag=test_tag,
            full_toggle=False,
        )
    )

    assert reminder_cache_transaction_detail.id is not None
    assert reminder_cache_transaction_detail.tag is not None
    test_tag.delete()
    reminder_cache_transaction_detail.refresh_from_db()
    assert reminder_cache_transaction_detail.tag is None
