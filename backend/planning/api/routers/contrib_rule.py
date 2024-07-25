from ninja import Router
from planning.api.views.contrib_rule import contrib_rule_router

router = Router()
router.add_router("/", contrib_rule_router)
