from ninja import Router
from tags.api.views.tag_graph import tag_graph_router

router = Router()
router.add_router("/", tag_graph_router)
