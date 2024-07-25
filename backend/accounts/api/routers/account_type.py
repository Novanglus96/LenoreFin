from ninja import Router
from accounts.api.views.account_type import account_type_router

router = Router()
router.add_router("/", account_type_router)
