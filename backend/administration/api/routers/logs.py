from ninja import Router
from administration.api.views.logs import logs_router

router = Router()
router.add_router("/", logs_router)
