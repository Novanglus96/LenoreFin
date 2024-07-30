from ninja import Router
from tags.api.views.graph_by_tags import graph_by_tags_router

router = Router()
router.add_router("/", graph_by_tags_router)
