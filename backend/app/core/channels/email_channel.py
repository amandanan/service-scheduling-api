from app.core import email as _email
from app.core.notification_channel import Notification, NotificationChannel


class EmailChannel(NotificationChannel):
    """Send via SMTP e-mail.

    Delegates to app.core.email.send_email which:
      - returns False when SMTP_HOST is not set
      - returns True  when the message was accepted by the server
      - raises        when the SMTP handshake fails
    """

    name = "email"

    def send(self, notification: Notification) -> bool:
        if not notification.recipient_email:
            return False
        return _email.send_email(
            notification.recipient_email,
            notification.subject,
            notification.body,
        )
