from app.core import whatsapp as _whatsapp
from app.core.notification_channel import Notification, NotificationChannel


class WhatsAppChannel(NotificationChannel):
    """Send via WhatsApp (evolution / zapi / generic provider).

    Delegates to app.core.whatsapp.send_whatsapp which:
      - returns False when WHATSAPP_API_URL is not set
      - returns True  when the provider accepted the message
      - raises        when the provider returned an error
    """

    name = "whatsapp"

    def send(self, notification: Notification) -> bool:
        if not notification.recipient_phone:
            return False
        return _whatsapp.send_whatsapp(notification.recipient_phone, notification.body)
