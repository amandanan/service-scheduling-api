"""Notification service: builds messages and delivers them through channels.

The service tries channels in the order given at construction time and stops
at the first that returns True ("delivered"). This gives a WhatsApp-first /
e-mail-fallback behaviour without any knowledge of the specific channels.

Public API (unchanged callers):
  send_booking_confirmation(db, appointment, business, service, professional, client)
  send_appointment_reminder(db, appointment, business, service, professional, client)
  send_password_reset(user, reset_token)
"""

import logging
import os

from sqlalchemy.orm import Session

from app.core import email
from app.core.notification_channel import Notification, NotificationChannel
from app.models.appointment import Appointment
from app.models.client import Client
from app.models.notification_log import NotificationLog
from app.models.professional import Professional
from app.models.service import Service
from app.models.user import User

logger = logging.getLogger(__name__)


# ── Internal helpers ───────────────────────────────────────────────────────────

def _frontend_url() -> str:
    return os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")


def _manage_url(public_token: str) -> str:
    return f"{_frontend_url()}/agendamento/{public_token}"


def _appointment_message(
    greeting: str,
    appointment: Appointment,
    business: User,
    service: Service,
    professional: Professional,
) -> str:
    return (
        f"{greeting}\n\n"
        f"Serviço: {service.name}\n"
        f"Profissional: {professional.name}\n"
        f"Data: {appointment.scheduled_at.strftime('%d/%m/%Y')}\n"
        f"Horário: {appointment.scheduled_at.strftime('%H:%M')}\n\n"
        f"Para cancelar ou remarcar, acesse:\n{_manage_url(appointment.public_token)}\n\n"
        f"{business.full_name}"
    )


def _log(
    db: Session,
    client: Client,
    channel: str,
    notification_type: str,
    status: str,
    appointment_id: int | None = None,
) -> None:
    db.add(NotificationLog(
        owner_id=client.owner_id,
        client_id=client.id,
        channel=channel,
        notification_type=notification_type,
        status=status,
        appointment_id=appointment_id,
    ))


# ── NotificationService ────────────────────────────────────────────────────────

class NotificationService:
    """Delivers a Notification through an ordered list of channels.

    Channels are tried in priority order; the first to return True stops the
    chain ("fallback"). Channels that return False are logged as
    "skipped_not_configured"; channels that raise are logged as "failed".
    Channels after a successful delivery are never attempted.
    """

    def __init__(self, channels: list[NotificationChannel]) -> None:
        self.channels = channels

    def deliver(
        self,
        db: Session,
        client: Client,
        notification: Notification,
    ) -> None:
        if not client.notification_consent:
            _log(db, client, "-", notification.notification_type, "skipped_no_consent",
                 notification.appointment_id)
            db.commit()
            return

        for channel in self.channels:
            try:
                ok = channel.send(notification)
                status = "sent" if ok else "skipped_not_configured"
            except Exception:
                logger.exception("Channel %r failed for %s", channel.name, notification.notification_type)
                status = "failed"

            _log(db, client, channel.name, notification.notification_type, status,
                 notification.appointment_id)

            if status == "sent":
                break   # delivered — don't try lower-priority channels

        db.commit()


def _default_service() -> NotificationService:
    """Build the live service: WhatsApp first, e-mail as fallback."""
    from app.core.channels.whatsapp_channel import WhatsAppChannel
    from app.core.channels.email_channel import EmailChannel

    return NotificationService([WhatsAppChannel(), EmailChannel()])


# ── Public notification functions ──────────────────────────────────────────────

def send_password_reset(user: User, reset_token: str) -> None:
    """E-mail a password-reset link to a business owner (always uses e-mail)."""
    if not user.email:
        return

    reset_url = f"{_frontend_url()}/redefinir-senha/{reset_token}"
    subject = "Redefinição de senha"
    body = (
        f"Olá {user.full_name},\n\n"
        f"Recebemos um pedido para redefinir a senha da sua conta.\n"
        f"Acesse o link abaixo para criar uma nova senha (expira em 1 hora):\n\n"
        f"{reset_url}\n\n"
        f"Se você não solicitou, ignore este e-mail."
    )
    email.send_email(user.email, subject, body)


def send_booking_confirmation(
    db: Session,
    appointment: Appointment,
    business: User,
    service: Service,
    professional: Professional,
    client: Client,
    *,
    _service: NotificationService | None = None,
) -> None:
    notification = Notification(
        notification_type="confirmation",
        subject=f"Agendamento confirmado - {business.full_name}",
        body=_appointment_message(
            f"Olá {client.full_name}, seu agendamento foi confirmado:",
            appointment, business, service, professional,
        ),
        recipient_name=client.full_name,
        recipient_phone=client.phone or None,
        recipient_email=client.email or None,
        appointment_id=appointment.id,
    )
    (_service or _default_service()).deliver(db, client, notification)


def send_appointment_reminder(
    db: Session,
    appointment: Appointment,
    business: User,
    service: Service,
    professional: Professional,
    client: Client,
    *,
    _service: NotificationService | None = None,
) -> None:
    notification = Notification(
        notification_type="reminder",
        subject=f"Lembrete de agendamento - {business.full_name}",
        body=_appointment_message(
            f"Olá {client.full_name}, este é um lembrete do seu agendamento:",
            appointment, business, service, professional,
        ),
        recipient_name=client.full_name,
        recipient_phone=client.phone or None,
        recipient_email=client.email or None,
        appointment_id=appointment.id,
    )
    (_service or _default_service()).deliver(db, client, notification)
