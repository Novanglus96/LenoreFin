from ninja import Router
from accounts.api.views.forecast import forecast_router

router = Router()
router.add_router("/", forecast_router)
