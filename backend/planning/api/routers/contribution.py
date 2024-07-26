from ninja import Router
from planning.api.views.contribution import contribution_router

router = Router()
router.add_router("/", contribution_router)
