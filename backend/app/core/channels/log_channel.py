import logging

from app.core.notification_channel import Notification, NotificationChannel

logger = logging.getLogger(__name__)


class LogChannel(NotificationChannel):
    """No-op channel that just logs the notification.

    Useful in tests and local dev to verify the notification pipeline
    without any external dependency. Always returns True (= "delivered").
    """

    name = "log"

    def send(self, notification: Notification) -> bool:
        logger.info(
            "LogChannel [%s] → %s (%s): %s",
            notification.notification_type,
            notification.recipient_name,
            notification.recipient_phone or notification.recipient_email or "no contact",
            notification.body[:120],
        )
        return True
