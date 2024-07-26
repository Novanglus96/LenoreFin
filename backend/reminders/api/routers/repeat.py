from ninja import Router
from reminders.api.views.repeat import repeat_router

router = Router()
router.add_router("/", repeat_router)
