import json
import logging
from typing import Iterable, Optional

from django.conf import settings

try:
    from pywebpush import WebPushException, webpush
except ImportError:  # pragma: no cover - fallback if dependency missing
    WebPushException = Exception  # type: ignore
    webpush = None  # type: ignore

logger = logging.getLogger(__name__)


def is_webpush_enabled() -> bool:
    return bool(
        getattr(settings, "WEBPUSH_ENABLED", False)
        and getattr(settings, "WEBPUSH_VAPID_PUBLIC_KEY", "")
        and getattr(settings, "WEBPUSH_VAPID_PRIVATE_KEY", "")
        and getattr(settings, "WEBPUSH_VAPID_CLAIM", "")
        and webpush
    )


def _send_to_subscription(subscription, payload: dict) -> bool:
    if not is_webpush_enabled():
        return False

    subscription_info = {
        "endpoint": subscription.endpoint,
        "keys": {
            "p256dh": subscription.p256dh_key,
            "auth": subscription.auth_key,
        },
    }

    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=settings.WEBPUSH_VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.WEBPUSH_VAPID_CLAIM},
        )
        return True
    except WebPushException as exc:  # pragma: no cover - network dependent
        logger.warning("Web push failed (%s): %s", exc.__class__.__name__, exc)
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None)

        # Remove stale subscriptions
        if status_code in (401, 404, 410):
            subscription.is_active = False
            subscription.save(update_fields=["is_active"])
            logger.info("Disabled stale push subscription: %s", subscription.endpoint)
        return False
    except Exception as exc:  # pragma: no cover - network dependent
        logger.exception("Unexpected web push error: %s", exc)
        return False


def send_push_notification(
    email: str,
    title: str,
    body: str,
    *,
    data: Optional[dict] = None,
    tag: Optional[str] = None,
) -> bool:
    """
    Send push notification to all active subscriptions for given email.
    Returns True if at least one subscription succeeded.
    """
    if not is_webpush_enabled():
        logger.debug("Web push disabled or not configured; skipping notification for %s", email)
        return False

    from .models import NotificationSubscription  # lazy import to avoid circular deps

    subscriptions = NotificationSubscription.objects.filter(email=email, is_active=True)
    if not subscriptions.exists():
        logger.debug("No active push subscriptions for %s", email)
        return False

    payload = {
        "title": title,
        "body": body,
        "tag": tag or "notification",
        "data": data or {},
    }

    success = False
    for subscription in subscriptions:
        delivered = _send_to_subscription(subscription, payload)
        success = success or delivered

    return success


def broadcast_push_notification(
    emails: Iterable[str],
    title: str,
    body: str,
    *,
    data: Optional[dict] = None,
    tag: Optional[str] = None,
) -> int:
    """
    Send push notification to multiple emails.
    Returns number of emails for which at least one notification succeeded.
    """
    delivered_count = 0
    for email in set(filter(None, emails)):
        if send_push_notification(email, title, body, data=data, tag=tag):
            delivered_count += 1
    return delivered_count



