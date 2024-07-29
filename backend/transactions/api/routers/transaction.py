from ninja import Router
from transactions.api.views.transaction import transaction_router

router = Router()
router.add_router("/", transaction_router)
