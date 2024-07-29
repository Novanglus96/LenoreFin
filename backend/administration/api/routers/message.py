from ninja import Router
from administration.api.views.message import message_router

router = Router()
router.add_router("/", message_router)
