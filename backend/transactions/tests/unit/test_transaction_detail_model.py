import pytest
from transactions.models import TransactionDetail


@pytest.mark.django_db
def test_transaction_detail_creation(test_transaction, test_tag):
    transaction_detail = TransactionDetail.objects.create(
        transaction=test_transaction,
        detail_amt=1.00,
        tag=test_tag,
        full_toggle=False,
    )

    assert transaction_detail.id is not None
    assert transaction_detail.transaction == test_transaction
    assert transaction_detail.detail_amt == 1.00
    assert transaction_detail.tag == test_tag
    assert not transaction_detail.full_toggle


@pytest.mark.django_db
def test_transaction_detail_defaults(test_transaction, test_tag):
    transaction_detail = TransactionDetail.objects.create(
        transaction=test_transaction,
        tag=test_tag,
    )

    assert transaction_detail.id is not None
    assert transaction_detail.detail_amt == 0.00
    assert not transaction_detail.full_toggle


@pytest.mark.django_db
def test_transaction_foreign_key_cascade_delete(test_tag, test_transaction):
    TransactionDetail.objects.create(
        transaction=test_transaction,
        detail_amt=1.00,
        tag=test_tag,
        full_toggle=False,
    )

    assert TransactionDetail.objects.count() == 1
    test_transaction.delete()
    assert TransactionDetail.objects.count() == 0


@pytest.mark.django_db
def test_tag_foreign_key_set_null_delete(test_tag, test_transaction):
    transaction_detail = TransactionDetail.objects.create(
        transaction=test_transaction,
        detail_amt=1.00,
        tag=test_tag,
        full_toggle=False,
    )

    assert transaction_detail.id is not None
    assert transaction_detail.tag is not None
    test_tag.delete()
    transaction_detail.refresh_from_db()
    assert transaction_detail.tag is None
