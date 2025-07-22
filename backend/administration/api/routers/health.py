from ninja import Router
from administration.api.views.health import health_router

router = Router()
router.add_router("/", health_router)
