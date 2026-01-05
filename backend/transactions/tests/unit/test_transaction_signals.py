import pytest
from unittest.mock import patch, call
from django.core.files.uploadedfile import SimpleUploadedFile
from transactions.models import TransactionImage
from core.cache.keys import (
    account_financials,
    account_real_transactions,
    account_all_balances,
    account_combined_transactions,
)


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

    expected_calls = [
        call(account_combined_transactions(test_transaction.source_account.id)),
        call(account_all_balances(test_transaction.source_account.id)),
        call(account_financials(test_transaction.source_account.id)),
        call(account_real_transactions(test_transaction.source_account.id)),
    ]

    mock_delete_pattern.assert_has_calls(
        expected_calls,
        any_order=True,
    )

    assert mock_delete_pattern.call_count == 4


@pytest.mark.django_db
@patch("transactions.signals.delete_pattern")
def test_transaction_save_invalidates_both_account_caches(
    mock_delete_pattern, test_transaction, test_savings_account
):
    test_transaction.destination_account = test_savings_account
    test_transaction.save()

    expected_calls = [
        call(account_combined_transactions(test_transaction.source_account.id)),
        call(account_all_balances(test_transaction.source_account.id)),
        call(account_financials(test_transaction.source_account.id)),
        call(account_real_transactions(test_transaction.source_account.id)),
        call(
            account_combined_transactions(
                test_transaction.destination_account.id
            )
        ),
        call(account_all_balances(test_transaction.destination_account.id)),
        call(account_financials(test_transaction.destination_account.id)),
        call(
            account_real_transactions(test_transaction.destination_account.id)
        ),
    ]

    mock_delete_pattern.assert_has_calls(expected_calls, any_order=True)
    assert mock_delete_pattern.call_count == 8


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
        call(account_combined_transactions(source_id)),
        call(account_all_balances(source_id)),
        call(account_financials(source_id)),
        call(account_real_transactions(source_id)),
        call(account_combined_transactions(dest_id)),
        call(account_all_balances(dest_id)),
        call(account_financials(dest_id)),
        call(account_real_transactions(dest_id)),
    ]

    mock_delete_pattern.assert_has_calls(expected_calls, any_order=True)
    assert mock_delete_pattern.call_count == 8


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
