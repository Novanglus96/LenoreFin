from ninja import Router
from transactions.api.views.paycheck import paycheck_router

router = Router()
router.add_router("/", paycheck_router)
