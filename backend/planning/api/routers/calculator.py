from ninja import Router
from planning.api.views.calculator import calculator_router

router = Router()
router.add_router("/", calculator_router)
