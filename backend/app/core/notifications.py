import os

from sqlalchemy.orm import Session

from app.core import email
from app.core import whatsapp
from app.models.appointment import Appointment
from app.models.client import Client
from app.models.professional import Professional
from app.models.service import Service
from app.models.user import User
from app.models.notification_log import NotificationLog


def _frontend_url() -> str:
    return os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")


def _manage_url(public_token: str) -> str:
    return f"{_frontend_url()}/agendamento/{public_token}"


def send_password_reset(user: User, reset_token: str) -> None:
    """E-mail a password reset link to a business owner."""

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


def _log(db: Session, client: Client, channel: str, notification_type: str, status: str) -> None:
    db.add(NotificationLog(
        owner_id=client.owner_id,
        client_id=client.id,
        channel=channel,
        notification_type=notification_type,
        status=status,
    ))


def _notify(db: Session, client: Client, subject: str, body: str, notification_type: str) -> None:
    """Deliver a notification over every channel the client allows, respecting
    the client's LGPD consent, and record each attempt for auditing."""

    if not client.notification_consent:
        _log(db, client, "-", notification_type, "skipped_no_consent")
        db.commit()
        return

    if client.email:
        email.send_email(client.email, subject, body)
        _log(db, client, "email", notification_type, "sent")

    if client.phone:
        whatsapp.send_whatsapp(client.phone, body)
        _log(db, client, "whatsapp", notification_type, "sent")

    db.commit()


def send_booking_confirmation(
    db: Session,
    appointment: Appointment,
    business: User,
    service: Service,
    professional: Professional,
    client: Client,
) -> None:

    subject = f"Agendamento confirmado - {business.full_name}"

    body = _appointment_message(
        f"Olá {client.full_name}, seu agendamento foi confirmado:",
        appointment,
        business,
        service,
        professional,
    )

    _notify(db, client, subject, body, "confirmation")


def send_appointment_reminder(
    db: Session,
    appointment: Appointment,
    business: User,
    service: Service,
    professional: Professional,
    client: Client,
) -> None:
    """Reminder for an upcoming appointment, sent by e-mail and WhatsApp."""

    subject = f"Lembrete de agendamento - {business.full_name}"

    body = _appointment_message(
        f"Olá {client.full_name}, este é um lembrete do seu agendamento:",
        appointment,
        business,
        service,
        professional,
    )

    _notify(db, client, subject, body, "reminder")
