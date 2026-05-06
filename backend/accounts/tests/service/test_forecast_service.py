import pytest
from accounts.services import get_account_forecast
from accounts.dto import DomainForecast


@pytest.mark.django_db
@pytest.mark.service
def test_get_account_forecast_returns_domain_forecast(test_checking_account):
    result = get_account_forecast(test_checking_account.id, 7, 7)

    assert isinstance(result, DomainForecast)
    assert len(result.labels) == 15
    assert len(result.datasets) == 1
    assert len(result.datasets[0].data) == 15


@pytest.mark.django_db
@pytest.mark.service
def test_get_account_forecast_zero_interval(test_checking_account):
    result = get_account_forecast(test_checking_account.id, 0, 0)

    assert isinstance(result, DomainForecast)
    assert len(result.labels) == 1
    assert len(result.datasets[0].data) == 1


@pytest.mark.django_db
@pytest.mark.service
def test_get_account_forecast_nonexistent_account():
    result = get_account_forecast(9999, 7, 7)

    assert isinstance(result, DomainForecast)
    assert len(result.labels) == 15
    # All balances should be zero for a missing account
    assert all(v == 0 for v in result.datasets[0].data)


@pytest.mark.django_db
@pytest.mark.service
def test_get_account_forecast_dataset_styling(test_checking_account):
    result = get_account_forecast(test_checking_account.id, 3, 3)

    dataset = result.datasets[0]
    assert dataset.borderColor == "#212121"
    assert dataset.backgroundColor == "#212121"
    assert dataset.fill is not None
    assert dataset.fill.above == "rgb(76, 175, 80)"
    assert dataset.fill.below == "rgb(255, 52, 7)"
    assert dataset.fill.target.value == 0
