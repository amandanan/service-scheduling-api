"""Channel abstraction for the notification system.

NotificationChannel defines the contract every delivery channel must fulfil.
Notification is the payload passed between the business logic and the channels.

Fallback order is determined by the list supplied to NotificationService:
the service tries channels in order and stops at the first that returns True.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Notification:
    notification_type: str       # "confirmation" | "reminder"
    subject: str                 # used by e-mail; WhatsApp ignores it
    body: str                    # the full message text
    recipient_name: str
    recipient_phone: str | None
    recipient_email: str | None
    appointment_id: int | None = field(default=None)


class NotificationChannel(ABC):
    """Deliver a Notification over one specific transport.

    Contract:
      - Returns True  → message was accepted by the provider.
      - Returns False → channel is not configured or has no recipient address
                        for this notification; caller should try the next one.
      - Raises        → channel is configured and was attempted but failed
                        (network error, API rejection, …); caller logs "failed"
                        and tries the next channel.
    """

    name: str  # "whatsapp" | "email" | "log" | …

    @abstractmethod
    def send(self, notification: Notification) -> bool: ...
