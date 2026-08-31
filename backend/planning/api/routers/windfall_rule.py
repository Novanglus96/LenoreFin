from ninja import Router
from planning.api.views.windfall_rule import windfall_rule_router

router = Router()
router.add_router("/", windfall_rule_router)
