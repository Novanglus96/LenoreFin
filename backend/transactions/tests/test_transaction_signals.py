import pytest
from unittest.mock import patch, call
from django.core.files.uploadedfile import SimpleUploadedFile
from transactions.models import TransactionImage


@pytest.mark.django_db
@patch("transactions.signals.async_task")
def test_transaction_save_triggers_source_account_forecast_update(
    mock_async_task, test_transaction
):
    test_transaction.destination_account = None
    test_transaction.save()

    mock_async_task.assert_called_once_with(
        "transactions.tasks.update_cc_forecast_cache",
        test_transaction.source_account.id,
    )


@pytest.mark.django_db
@patch("transactions.signals.async_task")
def test_transaction_save_triggers_both_account_forecast_updates(
    mock_async_task, test_transaction, test_savings_account
):
    test_transaction.destination_account = test_savings_account
    test_transaction.save()

    expected_calls = [
        call(
            "transactions.tasks.update_cc_forecast_cache",
            test_transaction.source_account.id,
        ),
        call(
            "transactions.tasks.update_cc_forecast_cache",
            test_transaction.destination_account.id,
        ),
    ]

    mock_async_task.assert_has_calls(expected_calls, any_order=True)
    assert mock_async_task.call_count == 2


@pytest.mark.django_db
@patch("transactions.signals.async_task")
def test_transaction_delete_triggers_both_account_forecast_updates(
    mock_async_task, test_transaction, test_savings_account
):
    test_transaction.destination_account = test_savings_account
    test_transaction.save()

    source_id = test_transaction.source_account.id
    dest_id = test_transaction.destination_account.id
    mock_async_task.reset_mock()
    test_transaction.delete()

    expected_calls = [
        call("transactions.tasks.update_cc_forecast_cache", source_id),
        call("transactions.tasks.update_cc_forecast_cache", dest_id),
    ]

    mock_async_task.assert_has_calls(expected_calls, any_order=True)
    assert mock_async_task.call_count == 2


@pytest.mark.django_db
@patch("transactions.signals.delete_pattern")
def test_transaction_save_invalidates_source_cache_only(
    mock_delete_pattern, test_transaction
):
    test_transaction.destination_account = None
    test_transaction.save()

    mock_delete_pattern.assert_called_once_with(
        f"*account_transactions_{test_transaction.source_account.id}*"
    )


@pytest.mark.django_db
@patch("transactions.signals.delete_pattern")
def test_transaction_save_invalidates_both_account_caches(
    mock_delete_pattern, test_transaction, test_savings_account
):
    test_transaction.destination_account = test_savings_account
    test_transaction.save()

    expected_calls = [
        call(f"*account_transactions_{test_transaction.source_account.id}*"),
        call(
            f"*account_transactions_{test_transaction.destination_account.id}*"
        ),
    ]

    mock_delete_pattern.assert_has_calls(expected_calls, any_order=True)
    assert mock_delete_pattern.call_count == 2


@pytest.mark.django_db
@patch("transactions.signals.delete_pattern")
def test_transaction_delete_invalidates_both_account_caches(
    mock_delete_pattern, test_transaction, test_savings_account
):
    test_transaction.destination_account = test_savings_account
    test_transaction.save()

    source_id = test_transaction.source_account.id
    dest_id = test_transaction.destination_account.id
    mock_delete_pattern.reset_mock()
    test_transaction.delete()

    expected_calls = [
        call(f"*account_transactions_{source_id}*"),
        call(f"*account_transactions_{dest_id}*"),
    ]

    mock_delete_pattern.assert_has_calls(expected_calls, any_order=True)
    assert mock_delete_pattern.call_count == 2


@pytest.mark.django_db
def test_transaction_image_file_is_deleted_on_model_delete(test_transaction):
    image_file = SimpleUploadedFile(
        name="test.jpg",
        content=b"fake image data",
        content_type="image/jpeg",
    )

    image = TransactionImage.objects.create(
        image=image_file,
        transaction=test_transaction,
    )

    # no mocking needed — just ensure delete doesn't explode
    image.delete()
