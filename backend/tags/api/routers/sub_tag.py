from ninja import Router
from tags.api.views.sub_tag import sub_tag_router

router = Router()
router.add_router("/", sub_tag_router)
