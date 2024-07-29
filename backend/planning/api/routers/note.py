from ninja import Router
from planning.api.views.note import note_router

router = Router()
router.add_router("/", note_router)
