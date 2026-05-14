import pytest
from unittest.mock import patch, call
from django.core.files.uploadedfile import SimpleUploadedFile
from transactions.models import TransactionImage
from core.cache.keys import account_all


@pytest.mark.django_db
@patch("transactions.signals._refresh_account")
def test_transaction_save_triggers_source_account_refresh(
    mock_refresh, test_transaction
):
    test_transaction.destination_account = None
    test_transaction.save()

    mock_refresh.assert_called_once_with(test_transaction.source_account_id)


@pytest.mark.django_db
@patch("transactions.signals._refresh_account")
def test_transaction_save_triggers_both_account_refreshes(
    mock_refresh, test_transaction, test_savings_account
):
    test_transaction.destination_account = test_savings_account
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
    mock_refresh, test_transaction, test_savings_account
):
    test_transaction.destination_account = test_savings_account
    test_transaction.save()

    source_id = test_transaction.source_account_id
    dest_id = test_transaction.destination_account_id
    mock_refresh.reset_mock()
    test_transaction.delete()

    expected_calls = [call(source_id), call(dest_id)]
    mock_refresh.assert_has_calls(expected_calls, any_order=True)
    assert mock_refresh.call_count == 2


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
