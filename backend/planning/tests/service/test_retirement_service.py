import pytest
from planning.services import get_retirement_forecast
from planning.dto import DomainForecast


@pytest.mark.django_db
@pytest.mark.service
def test_get_retirement_forecast_returns_domain_forecast():
    result = get_retirement_forecast()

    assert isinstance(result, DomainForecast)
    assert isinstance(result.labels, list)
    assert isinstance(result.datasets, list)
    assert len(result.labels) == len(result.datasets[0].data)


@pytest.mark.django_db
@pytest.mark.service
def test_get_retirement_forecast_total_dataset_always_present():
    result = get_retirement_forecast()

    assert len(result.datasets) >= 1
    assert result.datasets[0].label == "Total"


@pytest.mark.django_db
@pytest.mark.service
def test_get_retirement_forecast_covers_full_year():
    from datetime import date
    from utils.dates import get_todays_date_timezone_adjusted

    result = get_retirement_forecast()
    today = get_todays_date_timezone_adjusted()
    jan_1st = date(today.year, 1, 1)
    dec_31st = date(today.year, 12, 31)
    expected_days = (dec_31st - jan_1st).days + 1

    assert len(result.labels) == expected_days
