from ninja import Router
from transactions.api.views.transaction_image import transaction_image_router

router = Router()
router.add_router("/", transaction_image_router)
