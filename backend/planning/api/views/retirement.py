from ninja import Router
from ninja.errors import HttpError
from typing import List
from planning.api.schemas.retirement import DatasetObject, ForecastOut, RetirementTransactionOut
from planning.services import get_retirement_forecast
from planning.services.retirement import get_retirement_transactions
import logging

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

retirement_router = Router(tags=["Retirement"])


@retirement_router.get("/get", response=ForecastOut)
def get_forecast(request):
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
                fill=ds.fill,
            )
            for ds in domain.datasets
        ]
        api_logger.debug("Forecast retrieved")
        return ForecastOut(labels=domain.labels, datasets=datasets)
    except Exception as e:
        api_logger.error("Forecast not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error : {str(e)}")


@retirement_router.get("/transactions", response=List[RetirementTransactionOut])
def get_transactions(request):
    try:
        transactions = get_retirement_transactions()
        api_logger.debug("Retirement transactions retrieved")
        return transactions
    except Exception as e:
        api_logger.error("Retirement transactions not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error : {str(e)}")
