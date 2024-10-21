from ninja import Router
from planning.api.views.budget import budget_router

router = Router()
router.add_router("/", budget_router)
