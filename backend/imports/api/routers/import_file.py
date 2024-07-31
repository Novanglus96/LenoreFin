from ninja import Router
from imports.api.views.import_file import import_file_router

router = Router()
router.add_router("/", import_file_router)
