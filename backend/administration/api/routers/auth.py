from ninja import Router
from administration.api.views.auth import auth_router as router

auth_router = Router()
auth_router.add_router("", router)
