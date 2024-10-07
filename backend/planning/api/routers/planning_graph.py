from ninja import Router
from planning.api.views.planning_graph import planning_graph_router

router = Router()
router.add_router("/", planning_graph_router)
