from ninja import Router
from planning.api.views.bucket import bucket_router

router = Router()
router.add_router("/", bucket_router)
