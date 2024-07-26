from ninja import Router
from administration.api.views.error_level import error_level_router

router = Router()
router.add_router("/", error_level_router)
