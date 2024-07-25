from ninja import Router
from tags.api.views.tag_type import tag_type_router

router = Router()
router.add_router("/", tag_type_router)
