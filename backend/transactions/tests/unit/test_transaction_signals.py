import pytest
from unittest.mock import patch, call
from django.core.files.uploadedfile import SimpleUploadedFile
from transactions.models import TransactionImage
from core.cache.keys import account_all


# The refresh and the broadcast are deferred to commit rather than run per
# saved row, so these drive the callbacks the way Django would — nothing fires
# while the writing transaction is still open, which is the point.


@pytest.mark.django_db
@patch("transactions.signals._refresh_account")
def test_transaction_save_triggers_source_account_refresh(
    mock_refresh, test_transaction, django_capture_on_commit_callbacks
):
    test_transaction.destination_account = None
    with django_capture_on_commit_callbacks(execute=True):
        test_transaction.save()

    mock_refresh.assert_called_once_with(test_transaction.source_account_id)


@pytest.mark.django_db
@patch("transactions.signals._refresh_account")
def test_transaction_save_triggers_both_account_refreshes(
    mock_refresh,
    test_transaction,
    test_savings_account,
    django_capture_on_commit_callbacks,
):
    test_transaction.destination_account = test_savings_account
    with django_capture_on_commit_callbacks(execute=True):
        test_transaction.save()

    expected_calls = [
        call(test_transaction.source_account_id),
        call(test_transaction.destination_account_id),
    ]
    mock_refresh.assert_has_calls(expected_calls, any_order=True)
    assert mock_refresh.call_count == 2


@pytest.mark.django_db
@patch("transactions.signals._refresh_account")
def test_transaction_delete_triggers_both_account_refreshes(
    mock_refresh,
    test_transaction,
    test_savings_account,
    django_capture_on_commit_callbacks,
):
    test_transaction.destination_account = test_savings_account
    with django_capture_on_commit_callbacks(execute=True):
        test_transaction.save()

    source_id = test_transaction.source_account_id
    dest_id = test_transaction.destination_account_id
    mock_refresh.reset_mock()
    with django_capture_on_commit_callbacks(execute=True):
        test_transaction.delete()

    expected_calls = [call(source_id), call(dest_id)]
    mock_refresh.assert_has_calls(expected_calls, any_order=True)
    assert mock_refresh.call_count == 2


@pytest.mark.django_db
@patch("transactions.signals.broadcast_invalidate")
@patch("transactions.signals._refresh_account")
def test_a_bulk_write_broadcasts_once_and_refreshes_each_account_once(
    mock_refresh,
    mock_broadcast,
    test_transaction,
    test_checking_account,
    test_savings_account,
    test_expense_transaction_type,
    django_capture_on_commit_callbacks,
):
    """Twenty rows across two accounts: one broadcast, two refreshes.

    Per-row firing is what this replaces. An import or a reminder run moving a
    few hundred rows used to send a few hundred broadcasts describing a single
    change, and every open browser refetched eleven queries for each one.
    """
    from transactions.models import Transaction

    with django_capture_on_commit_callbacks(execute=True):
        for i in range(20):
            Transaction.objects.create(
                transaction_date=test_transaction.transaction_date,
                transaction_type=test_expense_transaction_type,
                source_account=test_checking_account,
                destination_account=test_savings_account,
                description=f"bulk {i}",
                total_amount="1.00",
            )

    assert mock_broadcast.call_count == 1
    assert sorted(c.args[0] for c in mock_refresh.call_args_list) == sorted(
        [test_checking_account.id, test_savings_account.id]
    )


@pytest.mark.django_db
@patch("transactions.signals.broadcast_invalidate")
@patch("transactions.signals._refresh_account")
def test_nothing_is_announced_until_the_write_commits(
    mock_refresh, mock_broadcast, test_transaction
):
    """The old version broadcast mid-transaction.

    A client told to refetch while the writing transaction was still open could
    read exactly the state the broadcast said had changed.
    """
    test_transaction.save()

    mock_refresh.assert_not_called()
    mock_broadcast.assert_not_called()


@pytest.mark.django_db
@patch("transactions.signals.async_task")
@patch("transactions.signals.delete_pattern")
def test_refresh_account_clears_cache_then_recalculates(
    mock_delete, mock_async_task, test_transaction
):
    from transactions.signals import _refresh_account
    _refresh_account(test_transaction.source_account_id)

    mock_delete.assert_called_once_with(account_all(test_transaction.source_account_id))
    mock_async_task.assert_any_call(
        "transactions.tasks.update_cc_forecast_cache",
        test_transaction.source_account_id,
    )
    mock_async_task.assert_any_call(
        "transactions.tasks.update_interest_forecast_cache",
        test_transaction.source_account_id,
    )


@pytest.mark.django_db(transaction=True)
@patch("transactions.signals.broadcast_invalidate")
@patch("transactions.signals._refresh_account")
def test_one_transfer_outside_a_block_still_broadcasts_once(
    mock_refresh,
    mock_broadcast,
    test_checking_account,
    test_savings_account,
    test_expense_transaction_type,
):
    """Batching must not make the common case worse.

    Outside `atomic()` every `on_commit` runs immediately, so registering one
    per account meant a single transfer — which touches two — announced itself
    twice. Both accounts are queued in one call for this reason.
    """
    from transactions.models import Transaction

    Transaction.objects.create(
        transaction_date="2026-01-01",
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        destination_account=test_savings_account,
        description="single transfer",
        total_amount="1.00",
    )

    assert mock_broadcast.call_count == 1
    assert mock_refresh.call_count == 2


@pytest.mark.django_db(transaction=True)
@patch("transactions.signals.broadcast_invalidate")
@patch("transactions.signals._refresh_account")
def test_a_rolled_back_write_does_not_disable_later_ones(
    mock_refresh,
    mock_broadcast,
    test_checking_account,
    test_savings_account,
    test_expense_transaction_type,
):
    """A rollback must not leave the thread unable to announce anything again.

    The first version of this batching guarded registration with a thread-local
    "already scheduled" flag that only the flush cleared. Django discards
    on_commit callbacks when a transaction rolls back, so the flush never ran,
    the flag stayed set, and every later write on that thread — a long-lived
    gunicorn worker — silently stopped refreshing caches and broadcasting.
    """
    from django.db import transaction as db_transaction
    from transactions.models import Transaction

    def make(description):
        return Transaction.objects.create(
            transaction_date="2026-01-01",
            transaction_type=test_expense_transaction_type,
            source_account=test_checking_account,
            destination_account=test_savings_account,
            description=description,
            total_amount="1.00",
        )

    class Rollback(Exception):
        pass

    try:
        with db_transaction.atomic():
            make("rolled back")
            raise Rollback
    except Rollback:
        pass

    assert mock_broadcast.call_count == 0

    make("committed")

    assert mock_broadcast.call_count == 1
    assert mock_refresh.call_count >= 1


@pytest.mark.django_db
def test_transaction_image_file_is_deleted_on_model_delete(test_transaction, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    image_file = SimpleUploadedFile(
        name="test.jpg",
        content=b"fake image data",
        content_type="image/jpeg",
    )

    image = TransactionImage.objects.create(
        image=image_file,
        transaction=test_transaction,
    )

    path = tmp_path / image.image.name
    assert path.exists()

    image.delete()

    assert not path.exists()


@pytest.mark.django_db
def test_transaction_image_file_is_deleted_on_transaction_cascade(
    test_transaction, tmp_path, settings
):
    """post_delete signal fires during CASCADE, cleaning up the file on disk."""
    settings.MEDIA_ROOT = tmp_path
    image_file = SimpleUploadedFile(
        name="cascade.jpg",
        content=b"fake image data",
        content_type="image/jpeg",
    )

    image = TransactionImage.objects.create(
        image=image_file,
        transaction=test_transaction,
    )

    path = tmp_path / image.image.name
    assert path.exists()

    # Deleting the transaction triggers CASCADE which fires the post_delete signal
    test_transaction.delete()

    assert not path.exists()
