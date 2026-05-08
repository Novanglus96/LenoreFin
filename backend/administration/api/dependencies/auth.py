from ninja.security import SessionAuth as NinjaSessionAuth
from ninja.errors import HttpError


class SessionAuth(NinjaSessionAuth):
    """Requires an authenticated Django session."""

    def __init__(self):
        super().__init__(csrf=False)

    def authenticate(self, request, token):
        if request.user.is_authenticated:
            return request.user
        return None


class FullAccessAuth(NinjaSessionAuth):
    """Requires an authenticated session AND membership in the Full Access group."""

    def __init__(self):
        super().__init__(csrf=False)

    def authenticate(self, request, token):
        if not request.user.is_authenticated:
            return None
        if request.user.groups.filter(name="Full Access").exists():
            return request.user
        raise HttpError(403, "Read-only access: this action is not permitted")
