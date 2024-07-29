from ninja import Router
from administration.api.views.payee import payee_router

router = Router()
router.add_router("/", payee_router)
