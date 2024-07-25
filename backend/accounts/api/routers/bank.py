from ninja import Router
from accounts.api.views.bank import bank_router

router = Router()
router.add_router("/", bank_router)
