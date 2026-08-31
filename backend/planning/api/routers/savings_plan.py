from ninja import Router
from planning.api.views.savings_plan import savings_plan_router

router = Router()
router.add_router("/", savings_plan_router)
