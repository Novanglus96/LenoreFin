import pytest
from datetime import date
from decimal import Decimal
from administration.models import DescriptionHistory
from transactions.models import Transaction
from transactions.api.schemas.transaction import TransactionIn
from transactions.services.transaction import (
    upsert_description_history,
    create_transaction_service,
    update_transaction_service,
)


def _make_payload(account_id, status_id, transaction_type_id, tag_id=None):
    """Build a minimal TransactionIn payload."""
    details = []
    if tag_id is not None:
        details = [
            {
                "tag_amt": "10.00",
                "tag_pretty_name": "Test Tag",
                "tag_id": tag_id,
                "tag_full_toggle": False,
            }
        ]
    return TransactionIn(
        transaction_date=date(2026, 1, 1),
        total_amount=Decimal("10.00"),
        status_id=status_id,
        memo=None,
        description="Test transaction",
        edit_date=date(2026, 1, 1),
        add_date=date(2026, 1, 1),
        transaction_type_id=transaction_type_id,
        paycheck_id=None,
        details=details or None,
        source_account_id=account_id,
        destination_account_id=None,
        paycheck=None,
        checkNumber=None,
    )


@pytest.mark.django_db
@pytest.mark.service
def test_upsert_description_history_creates_new():
    """Calling upsert_description_history with a new description creates a DescriptionHistory record."""
    assert not DescriptionHistory.objects.filter(
        description_normalized="brand new description"
    ).exists()

    upsert_description_history("Brand New Description", tag_id=None)

    record = DescriptionHistory.objects.get(
        description_normalized="brand new description"
    )
    assert record.description_pretty == "Brand New Description"
    assert record.tag_id is None


@pytest.mark.django_db
@pytest.mark.service
def test_upsert_description_history_updates_existing(test_tag):
    """Calling upsert_description_history on an existing description updates the tag_id."""
    DescriptionHistory.objects.create(
        description_normalized="existing description",
        description_pretty="Existing Description",
        tag_id=None,
    )

    upsert_description_history("Existing Description", tag_id=test_tag.id)

    record = DescriptionHistory.objects.get(
        description_normalized="existing description"
    )
    assert record.tag_id == test_tag.id


@pytest.mark.django_db
@pytest.mark.service
def test_create_transaction_service_creates_transaction(
    test_checking_account,
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_tag,
):
    """create_transaction_service persists a Transaction row to the database."""
    payload = _make_payload(
        account_id=test_checking_account.id,
        status_id=test_pending_transaction_status.id,
        transaction_type_id=test_expense_transaction_type.id,
        tag_id=test_tag.id,
    )

    before_count = Transaction.objects.count()
    create_transaction_service(payload)

    assert Transaction.objects.count() == before_count + 1
    created = Transaction.objects.latest("id")
    assert created.description == "Test transaction"
    assert created.source_account_id == test_checking_account.id


@pytest.mark.django_db
@pytest.mark.service
def test_update_transaction_service_changes_fields(
    test_transaction,
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_checking_account,
):
    """update_transaction_service updates the description and other fields on the existing transaction."""
    payload = TransactionIn(
        transaction_date=date(2026, 2, 1),
        total_amount=Decimal("99.00"),
        status_id=test_pending_transaction_status.id,
        memo="Updated memo",
        description="Updated description",
        edit_date=date(2026, 2, 1),
        add_date=date(2026, 2, 1),
        transaction_type_id=test_expense_transaction_type.id,
        paycheck_id=None,
        details=None,
        source_account_id=test_checking_account.id,
        destination_account_id=None,
        paycheck=None,
        checkNumber=None,
    )

    update_transaction_service(test_transaction.id, payload)

    test_transaction.refresh_from_db()
    assert test_transaction.description == "Updated description"
    assert test_transaction.memo == "Updated memo"
    assert test_transaction.total_amount == Decimal("99.00")


@pytest.mark.django_db
@pytest.mark.service
def test_update_transaction_service_raises_for_missing_transaction(
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_checking_account,
):
    """update_transaction_service raises Http404 when the transaction does not exist."""
    from django.http import Http404

    payload = TransactionIn(
        transaction_date=date(2026, 1, 1),
        total_amount=Decimal("10.00"),
        status_id=test_pending_transaction_status.id,
        memo=None,
        description="Does not matter",
        edit_date=date(2026, 1, 1),
        add_date=date(2026, 1, 1),
        transaction_type_id=test_expense_transaction_type.id,
        paycheck_id=None,
        details=None,
        source_account_id=test_checking_account.id,
        destination_account_id=None,
        paycheck=None,
        checkNumber=None,
    )

    with pytest.raises(Http404):
        update_transaction_service(999999, payload)
