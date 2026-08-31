from decimal import Decimal
import logging

from ninja import Router
from ninja.errors import HttpError

from planning.api.schemas.savings_plan import SavingsPlanOut
from planning.services.savings_plan import build_savings_plan

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

savings_plan_router = Router(tags=["Savings Plan"])


@savings_plan_router.get("/get", response=SavingsPlanOut)
def get_savings_plan(
    request,
    horizon_months: int = 12,
    buffer: Decimal | None = None,
):
    """
    The function `get_savings_plan` builds a savings plan and returns it.

    The plan is computed on request rather than stored: it is derived entirely
    from buckets, reminders, budgets and the forecast, and any of those
    can change between one call and the next. It costs one forecast pass per
    account, so it is slow by the standards of this API — several seconds — and
    the client caches it rather than polling.

    Args:
        request (HttpRequest): The HTTP request object.
        horizon_months (int): how far ahead to plan. Defaults to a year.
        buffer (Decimal): what the funding account must still hold at its
            lowest point. Defaults to the household's configured cushion.

    Returns:
        SavingsPlanOut: the allocation, the bridging schedule and the evidence.
    """

    try:
        plan = build_savings_plan(horizon_months=horizon_months, buffer=buffer)
        api_logger.debug("Savings plan built")
        return plan
    except Exception as e:
        api_logger.error("Savings plan not built")
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error : {str(e)}")
