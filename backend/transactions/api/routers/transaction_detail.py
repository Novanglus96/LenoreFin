from ninja import Router
from transactions.api.views.transaction_detail import transaction_detail_router

router = Router()
router.add_router("/", transaction_detail_router)
