from ninja import Router
from administration.api.views.log_entry import log_entry_router

router = Router()
router.add_router("/", log_entry_router)
