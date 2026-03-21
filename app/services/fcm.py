"""Firebase Cloud Messaging sender service.

Sends push notifications via FCM HTTP v1 API using a Firebase service account.
Falls back to logging in development mode when credentials are not configured.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.config import settings

logger = logging.getLogger("preprank.fcm")


@dataclass
class PushMessage:
    token: str
    title: str
    body: str
    data: dict[str, str] | None = None


_firebase_app = None


def _get_firebase_app():
    """Lazily initialize Firebase Admin SDK."""
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app

    if not settings.fcm_credentials_json:
        logger.info("FCM credentials not configured — push notifications will be logged only")
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials

        cred = credentials.Certificate(settings.fcm_credentials_json)
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized")
        return _firebase_app
    except Exception as e:
        logger.warning(f"Failed to initialize Firebase: {e}")
        return None


async def send_push(message: PushMessage) -> bool:
    """Send a single push notification.

    Returns True if sent successfully, False otherwise.
    """
    if not message.token:
        return False

    app = _get_firebase_app()

    if app is None:
        # Development mode — log instead of sending
        logger.info(f"[FCM DRY RUN] to={message.token[:20]}... title={message.title}")
        return True

    try:
        from firebase_admin import messaging

        fcm_message = messaging.Message(
            token=message.token,
            notification=messaging.Notification(
                title=message.title,
                body=message.body,
            ),
            data=message.data or {},
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    click_action="FLUTTER_NOTIFICATION_CLICK",
                    channel_id="preprank_default",
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        badge=1,
                        sound="default",
                    ),
                ),
            ),
        )

        response = messaging.send(fcm_message)
        logger.info(f"FCM sent: {response}")
        return True

    except Exception as e:
        logger.warning(f"FCM send failed: {e}")
        return False


async def send_push_batch(messages: list[PushMessage]) -> int:
    """Send multiple push notifications. Returns count of successful sends."""
    if not messages:
        return 0

    app = _get_firebase_app()

    if app is None:
        for msg in messages:
            logger.info(f"[FCM DRY RUN] to={msg.token[:20]}... title={msg.title}")
        return len(messages)

    try:
        from firebase_admin import messaging

        fcm_messages = [
            messaging.Message(
                token=msg.token,
                notification=messaging.Notification(
                    title=msg.title,
                    body=msg.body,
                ),
                data=msg.data or {},
            )
            for msg in messages
            if msg.token
        ]

        if not fcm_messages:
            return 0

        # FCM supports up to 500 messages per batch
        sent = 0
        for i in range(0, len(fcm_messages), 500):
            batch = fcm_messages[i:i + 500]
            response = messaging.send_each(batch)
            sent += response.success_count
            if response.failure_count:
                logger.warning(f"FCM batch: {response.success_count} sent, {response.failure_count} failed")

        return sent

    except Exception as e:
        logger.warning(f"FCM batch send failed: {e}")
        return 0
