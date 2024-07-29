from ninja import Router
from transactions.api.views.transaction_status import transaction_status_router

router = Router()
router.add_router("/", transaction_status_router)
