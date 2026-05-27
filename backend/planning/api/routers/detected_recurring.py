from ninja import Router
from planning.api.views.detected_recurring import detected_recurring_router

router = Router()
router.add_router("/", detected_recurring_router)
