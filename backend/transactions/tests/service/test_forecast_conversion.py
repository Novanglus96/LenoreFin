from decimal import Decimal

import pytest

from transactions.models import (
    ForecastCacheTransaction,
    ForecastCacheTransactionDetail,
    Transaction,
    TransactionDetail,
)
from transactions.services import (
    ForecastTransactionNotFound,
    clean_forecast_description,
    convert_forecast_transaction,
)


@pytest.fixture
def forecast_with_tag(
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_income_transaction_type,
    test_checking_account,
    test_tag,
):
    """A computed forecast row with one full-toggle detail, as the cc/interest
    generators produce.

    test_income_transaction_type is pulled in because create_transactions looks
    up the income type to decide the sign, and errors if it does not exist.
    """
    forecast = ForecastCacheTransaction.objects.create(
        status=test_pending_transaction_status,
        description="(Test Card Estimated Payment)",
        memo="projected",
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        total_amount=Decimal("-125.00"),
    )
    ForecastCacheTransactionDetail.objects.create(
        transaction=forecast,
        detail_amt=Decimal("-125.00"),
        tag=test_tag,
        full_toggle=True,
    )
    return forecast


@pytest.mark.django_db
@pytest.mark.service
def test_convert_creates_real_transaction(forecast_with_tag, test_checking_account):
    """The forecast row is carried across as-is into a real transaction."""
    convert_forecast_transaction(forecast_with_tag.id)

    created = Transaction.objects.get(description="Test Card Payment")
    assert created.total_amount == Decimal("-125.00")
    assert created.transaction_date == forecast_with_tag.transaction_date
    assert created.source_account_id == test_checking_account.id
    assert created.memo == "projected"
    assert created.status.slug == "pending"


@pytest.mark.django_db
@pytest.mark.service
def test_convert_removes_the_cache_row(forecast_with_tag):
    """The cache entry is dropped so the table reflects the change immediately."""
    convert_forecast_transaction(forecast_with_tag.id)

    assert not ForecastCacheTransaction.objects.filter(
        id=forecast_with_tag.id
    ).exists()
    # Details go with it, so no orphans are left behind.
    assert not ForecastCacheTransactionDetail.objects.filter(
        transaction_id=forecast_with_tag.id
    ).exists()


@pytest.mark.django_db
@pytest.mark.service
def test_convert_carries_tags_across(forecast_with_tag, test_tag):
    """Detail rows are recreated against the real transaction, sign preserved."""
    convert_forecast_transaction(forecast_with_tag.id)

    created = Transaction.objects.get(description="Test Card Payment")
    details = TransactionDetail.objects.filter(transaction_id=created.id)
    assert details.count() == 1
    detail = details.first()
    assert detail.tag_id == test_tag.id
    assert detail.full_toggle is True
    # create_transactions re-derives the sign from transaction_type, so an
    # expense must not come back positive after the round trip.
    assert detail.detail_amt == Decimal("-125.00")


@pytest.mark.django_db
@pytest.mark.service
def test_convert_untagged_forecast(
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_income_transaction_type,
    test_checking_account,
):
    """A forecast row with no details still converts."""
    forecast = ForecastCacheTransaction.objects.create(
        status=test_pending_transaction_status,
        description="(Test Savings Interest)",
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        total_amount=Decimal("-3.21"),
    )

    convert_forecast_transaction(forecast.id)

    created = Transaction.objects.get(description="Test Savings Interest")
    assert created.total_amount == Decimal("-3.21")
    assert not TransactionDetail.objects.filter(transaction_id=created.id).exists()


@pytest.mark.django_db
@pytest.mark.service
def test_convert_missing_forecast_raises(db):
    """A stale id from an already-converted row is reported, not swallowed."""
    with pytest.raises(ForecastTransactionNotFound):
        convert_forecast_transaction(999999)


@pytest.mark.django_db
@pytest.mark.service
def test_convert_leaves_other_forecasts_alone(
    forecast_with_tag,
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_checking_account,
):
    """Converting one row does not disturb the rest of the cache."""
    other = ForecastCacheTransaction.objects.create(
        status=test_pending_transaction_status,
        description="(Other Estimated Payment)",
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        total_amount=Decimal("-50.00"),
    )

    convert_forecast_transaction(forecast_with_tag.id)

    assert ForecastCacheTransaction.objects.filter(id=other.id).exists()
    assert not Transaction.objects.filter(description="Other Payment").exists()


@pytest.mark.django_db
@pytest.mark.api
def test_convert_endpoint_converts_batch(
    api_client,
    patch_auth_as_full_access,
    forecast_with_tag,
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_checking_account,
):
    """The endpoint takes a list and converts every id in it."""
    second = ForecastCacheTransaction.objects.create(
        status=test_pending_transaction_status,
        description="(Second Estimated Payment)",
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        total_amount=Decimal("-10.00"),
    )

    response = api_client.patch(
        "/transactions/convert-forecast",
        json={"forecast_transactions": [forecast_with_tag.id, second.id]},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert Transaction.objects.filter(description="Test Card Payment").exists()
    assert Transaction.objects.filter(description="Second Payment").exists()
    assert ForecastCacheTransaction.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.api
def test_convert_endpoint_missing_id_returns_404(
    api_client, patch_auth_as_full_access
):
    response = api_client.patch(
        "/transactions/convert-forecast",
        json={"forecast_transactions": [999999]},
    )

    assert response.status_code == 404


@pytest.mark.unit
@pytest.mark.parametrize(
    "raw,expected",
    [
        # The three formats the forecast generators actually emit.
        ("(Visa Estimated Payment)", "Visa Payment"),
        ("(Visa Estimated Interest)", "Visa Interest"),
        ("(Emergency Fund Estimated Interest)", "Emergency Fund Interest"),
        # Brackets without the word, and the word without brackets.
        ("(Test Savings Interest)", "Test Savings Interest"),
        ("Visa Estimated Payment", "Visa Payment"),
        # Nothing to strip is left alone.
        ("Groceries", "Groceries"),
        # Account names containing brackets mid-string are not mangled.
        ("(Visa (Joint) Estimated Payment)", "Visa (Joint) Payment"),
        # Defensive: empty and whitespace-only.
        ("", ""),
        ("   ", ""),
    ],
)
def test_clean_forecast_description(raw, expected):
    assert clean_forecast_description(raw) == expected
