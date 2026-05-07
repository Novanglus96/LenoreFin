from ninja import Router
from ninja.errors import HttpError
from planning.api.schemas.retirement import DatasetObject, ForecastOut
from planning.services import get_retirement_forecast
import logging

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

retirement_router = Router(tags=["Retirement"])


@retirement_router.get("/get", response=ForecastOut)
def get_forecast(request):
    """
    The function `get_forecast` retrieves the forecast data for the retirement
    accounts

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        ForecastOut: the forecast object
    """
    try:
        domain = get_retirement_forecast()
        datasets = [
            DatasetObject(
                borderColor=ds.borderColor,
                backgroundColor=ds.backgroundColor,
                tension=ds.tension,
                data=ds.data,
                pointStyle=ds.pointStyle,
                radius=ds.radius,
                hitRadius=ds.hitRadius,
                hoverRadius=ds.hoverRadius,
                label=ds.label,
            )
            for ds in domain.datasets
        ]
        api_logger.debug("Forecast retrieved")
        return ForecastOut(labels=domain.labels, datasets=datasets)
    except Exception as e:
        api_logger.error("Forecast not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error : {str(e)}")
