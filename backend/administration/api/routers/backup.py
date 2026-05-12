from ninja import Router
from administration.api.views.backup import backup_router

router = Router()
router.add_router("/", backup_router)
