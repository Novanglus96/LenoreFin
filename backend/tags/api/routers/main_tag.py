from ninja import Router
from tags.api.views.main_tag import main_tag_router

router = Router()
router.add_router("/", main_tag_router)
