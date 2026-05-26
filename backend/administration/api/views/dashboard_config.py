from ninja import Router
from ninja.errors import HttpError
from administration.models import UserDashboardConfig, DEFAULT_DASHBOARD_LAYOUT
from administration.api.schemas.dashboard_config import DashboardConfigIn, DashboardConfigOut
import logging

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

dashboard_config_router = Router(tags=["Dashboard Config"])


@dashboard_config_router.get("/", response=DashboardConfigOut)
def get_dashboard_config(request):
    config, _ = UserDashboardConfig.objects.get_or_create(
        user=request.user,
        defaults={"layout": DEFAULT_DASHBOARD_LAYOUT},
    )
    api_logger.debug(f"Dashboard config retrieved for user {request.user.username}")
    return config


@dashboard_config_router.patch("/", response=DashboardConfigOut)
def update_dashboard_config(request, payload: DashboardConfigIn):
    try:
        config, _ = UserDashboardConfig.objects.get_or_create(
            user=request.user,
            defaults={"layout": DEFAULT_DASHBOARD_LAYOUT},
        )
        config.layout = [w.dict() for w in payload.layout]
        config.save()
        api_logger.info(f"Dashboard config updated for user {request.user.username}")
        return config
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, "Dashboard config update error")
