import json
import logging
import os

error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")


def send_push_notifications(message_text, link=None, user=None):
    """
    Send a Web Push notification for a new inbox message.

    If user is given, only that user's subscriptions are targeted.
    If user is None (global message), all subscriptions are notified.
    Expired subscriptions (HTTP 410) are silently removed.
    A missing VAPID_PRIVATE_KEY skips push silently (opt-in feature).
    """
    private_key = os.environ.get("VAPID_PRIVATE_KEY")
    if not private_key:
        return

    from administration.models import PushSubscription
    from pywebpush import webpush, WebPushException

    email = os.environ.get("VAPID_EMAIL", "admin@example.com")
    claims = {"sub": f"mailto:{email}"}
    payload = json.dumps({"title": "LenoreFin", "body": message_text, "link": link or "/"})

    subs = PushSubscription.objects.all()
    if user is not None:
        subs = subs.filter(user=user)

    for sub in subs:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                },
                data=payload,
                vapid_private_key=private_key,
                vapid_claims=claims,
            )
        except WebPushException as e:
            if e.response is not None and e.response.status_code == 410:
                sub.delete()
            else:
                error_logger.exception(f"Push notification failed for subscription {sub.id}: {e}")
        except Exception as e:
            error_logger.exception(f"Unexpected push error for subscription {sub.id}: {e}")
