from ninja import Router
from administration.api.views.description_history import (
    description_history_router,
)

router = Router()
router.add_router("/", description_history_router)
