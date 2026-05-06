from ninja import Router
from ninja.errors import HttpError
from accounts.api.schemas.forecast import ForecastOut
from accounts.services import get_account_forecast
from accounts.mappers import domain_forecast_to_schema
import logging

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

forecast_router = Router(tags=["Account Forecasts"])


@forecast_router.get("/get/{account_id}", response=ForecastOut)
def get_forecast(
    request, account_id: int, start_interval: int, end_interval: int
):
    """
    The function `get_forecast` retrieves the forecast data for the account id

    Args:
        request (HttpRequest): The HTTP request object.
        account_id (int): The id of the account to retrieve forecast data.
        start_interval (int): the number of days before today to start forecast.
        end_interval (int): the number of days after today to end forecast.

    Returns:
        ForecastOut: the forecast object

    Raises:
        Http404: If the account with the specified ID does not exist.
    """
    try:
        domain_forecast = get_account_forecast(
            account_id, start_interval, end_interval
        )
        api_logger.debug("Forecast retrieved")
        return domain_forecast_to_schema(domain_forecast)
    except Exception as e:
        api_logger.error("Forecast not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error : {str(e)}")
