from ninja import Router
from transactions.api.views.transaction_type import transaction_type_router

router = Router()
router.add_router("/", transaction_type_router)
