import pytest
from transactions.models import ForecastCacheTransactionDetail


@pytest.mark.django_db
def test_forecast_cache_transaction_detail_creation(
    test_forecast_transaction, test_tag
):
    forecast_cache_transaction_detail = (
        ForecastCacheTransactionDetail.objects.create(
            transaction=test_forecast_transaction,
            detail_amt=1.00,
            tag=test_tag,
            full_toggle=False,
        )
    )

    assert forecast_cache_transaction_detail.id is not None
    assert (
        forecast_cache_transaction_detail.transaction
        == test_forecast_transaction
    )
    assert forecast_cache_transaction_detail.detail_amt == 1.00
    assert forecast_cache_transaction_detail.tag == test_tag
    assert not forecast_cache_transaction_detail.full_toggle


@pytest.mark.django_db
def test_forecast_cache_transaction_detail_defaults(
    test_forecast_transaction, test_tag
):
    forecast_cache_transaction_detail = (
        ForecastCacheTransactionDetail.objects.create(
            transaction=test_forecast_transaction,
            tag=test_tag,
        )
    )

    assert forecast_cache_transaction_detail.id is not None
    assert forecast_cache_transaction_detail.detail_amt == 0.00
    assert not forecast_cache_transaction_detail.full_toggle


@pytest.mark.django_db
def test_forecast_transaction_foreign_key_cascade_delete(
    test_tag, test_forecast_transaction
):
    ForecastCacheTransactionDetail.objects.create(
        transaction=test_forecast_transaction,
        detail_amt=1.00,
        tag=test_tag,
        full_toggle=False,
    )

    assert ForecastCacheTransactionDetail.objects.count() == 1
    test_forecast_transaction.delete()
    assert ForecastCacheTransactionDetail.objects.count() == 0


@pytest.mark.django_db
def test_tag_foreign_key_set_null_delete(test_tag, test_forecast_transaction):
    forecast_cache_transaction_detail = (
        ForecastCacheTransactionDetail.objects.create(
            transaction=test_forecast_transaction,
            detail_amt=1.00,
            tag=test_tag,
            full_toggle=False,
        )
    )

    assert forecast_cache_transaction_detail.id is not None
    assert forecast_cache_transaction_detail.tag is not None
    test_tag.delete()
    forecast_cache_transaction_detail.refresh_from_db()
    assert forecast_cache_transaction_detail.tag is None
