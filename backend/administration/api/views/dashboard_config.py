from ninja import Router
from ninja.errors import HttpError
from administration.models import (
    UserDashboardConfig,
    DEFAULT_DASHBOARD_LAYOUT,
    DEFAULT_GRAPH_WIDGETS,
)
from administration.api.schemas.dashboard_config import DashboardConfigIn, DashboardConfigOut
import logging

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

dashboard_config_router = Router(tags=["Dashboard Config"])


def _get_or_create_config(user):
    config, _ = UserDashboardConfig.objects.get_or_create(
        user=user,
        defaults={"layout": DEFAULT_DASHBOARD_LAYOUT, "graph_widgets": DEFAULT_GRAPH_WIDGETS},
    )

    dirty = False

    if not config.graph_widgets:
        config.graph_widgets = DEFAULT_GRAPH_WIDGETS
        dirty = True

    # Add any new widget slots that don't exist in the user's saved layout
    existing_ids = {w["id"] for w in config.layout}
    for default_widget in DEFAULT_DASHBOARD_LAYOUT:
        if default_widget["id"] not in existing_ids:
            config.layout.append(default_widget)
            dirty = True

    if dirty:
        config.save()

    return config


@dashboard_config_router.get("/", response=DashboardConfigOut)
def get_dashboard_config(request):
    config = _get_or_create_config(request.user)
    api_logger.debug(f"Dashboard config retrieved for user {request.user.username}")
    return config


@dashboard_config_router.patch("/", response=DashboardConfigOut)
def update_dashboard_config(request, payload: DashboardConfigIn):
    try:
        config = _get_or_create_config(request.user)
        if payload.layout is not None:
            config.layout = [w.dict() for w in payload.layout]
        if payload.graph_widgets is not None:
            config.graph_widgets = [w.dict() for w in payload.graph_widgets]
        config.save()
        api_logger.info(f"Dashboard config updated for user {request.user.username}")
        return config
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, "Dashboard config update error")
