from ninja import Router
from administration.api.views.option import option_router

router = Router()
router.add_router("/", option_router)
