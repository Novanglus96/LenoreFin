from ninja import Router
from planning.api.views.planner import planner_router

router = Router()
router.add_router("/", planner_router)
