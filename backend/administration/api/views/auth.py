from ninja import Router, Schema
from ninja.errors import HttpError
from django.contrib.auth import authenticate, login, logout
from administration.api.dependencies.auth import SessionAuth
import logging

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

auth_router = Router(tags=["Auth"])


class LoginIn(Schema):
    username: str
    password: str


class UserOut(Schema):
    id: int
    username: str
    group: str


def _user_group(user) -> str:
    if user.groups.filter(name="Full Access").exists():
        return "full_access"
    if user.groups.filter(name="Readonly").exists():
        return "readonly"
    return "readonly"


@auth_router.post("/login", auth=None)
def auth_login(request, payload: LoginIn):
    user = authenticate(request, username=payload.username, password=payload.password)
    if user is None:
        raise HttpError(401, "Invalid credentials")
    login(request, user)
    api_logger.info(f"User logged in: {user.username}")
    return UserOut(id=user.id, username=user.username, group=_user_group(user))


@auth_router.post("/logout", auth=SessionAuth())
def auth_logout(request):
    api_logger.info(f"User logged out: {request.user.username}")
    logout(request)
    return {"success": True}


@auth_router.get("/me", response=UserOut, auth=SessionAuth())
def auth_me(request):
    return UserOut(
        id=request.user.id,
        username=request.user.username,
        group=_user_group(request.user),
    )
