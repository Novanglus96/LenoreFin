from ninja import Router
from administration.api.views.dashboard_config import dashboard_config_router

router = Router()
router.add_router("/", dashboard_config_router)
