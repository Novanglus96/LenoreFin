from ninja import Router
from accounts.api.views.account import account_router

router = Router()
router.add_router("/", account_router)
