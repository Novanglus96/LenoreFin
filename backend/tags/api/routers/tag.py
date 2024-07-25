from ninja import Router
from tags.api.views.tag import tag_router

router = Router()
router.add_router("/", tag_router)
