import os
import logging
from ninja import Router
from ninja.errors import HttpError

from administration.models import PushSubscription
from administration.api.schemas.push_subscription import PushSubscribeIn, VapidPublicKeyOut

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

push_router = Router(tags=["Push Notifications"])


@push_router.get("/vapid-public-key", response=VapidPublicKeyOut, auth=None)
def get_vapid_public_key(request):
    key = os.environ.get("VAPID_PUBLIC_KEY", "")
    return {"public_key": key}


@push_router.post("/subscribe", response={200: dict})
def subscribe(request, payload: PushSubscribeIn):
    try:
        PushSubscription.objects.update_or_create(
            endpoint=payload.endpoint,
            defaults={
                "user": request.user,
                "p256dh": payload.p256dh,
                "auth": payload.auth,
            },
        )
        api_logger.info(f"Push subscription saved for user {request.user}")
        return {"success": True}
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, "Failed to save push subscription")


@push_router.delete("/unsubscribe", response={200: dict})
def unsubscribe(request):
    try:
        deleted, _ = PushSubscription.objects.filter(user=request.user).delete()
        api_logger.info(f"Push subscriptions removed for user {request.user} ({deleted})")
        return {"success": True}
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, "Failed to remove push subscription")


@push_router.get("/status", response={200: dict})
def subscription_status(request):
    has_sub = PushSubscription.objects.filter(user=request.user).exists()
    return {"subscribed": has_sub}
