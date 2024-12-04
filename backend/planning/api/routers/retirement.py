from ninja import Router
from planning.api.views.retirement import retirement_router

router = Router()
router.add_router("/", retirement_router)
