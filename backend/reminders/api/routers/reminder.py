from ninja import Router
from reminders.api.views.reminder import reminder_router

router = Router()
router.add_router("/", reminder_router)
