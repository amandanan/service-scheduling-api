import os

from app.core import email
from app.models.appointment import Appointment
from app.models.client import Client
from app.models.professional import Professional
from app.models.service import Service
from app.models.user import User


def _manage_url(public_token: str) -> str:
    base_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
    return f"{base_url}/agendamento/{public_token}"


def _appointment_email_body(
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


def send_booking_confirmation(
    appointment: Appointment,
    business: User,
    service: Service,
    professional: Professional,
    client: Client,
) -> None:

    if not client.email:
        return

    subject = f"Agendamento confirmado - {business.full_name}"

    body = _appointment_email_body(
        f"Olá {client.full_name}, seu agendamento foi confirmado:",
        appointment,
        business,
        service,
        professional,
    )

    email.send_email(client.email, subject, body)


def send_appointment_reminder(
    appointment: Appointment,
    business: User,
    service: Service,
    professional: Professional,
    client: Client,
) -> None:
    """Reminder email for an upcoming appointment.

    Not yet wired to a scheduler; intended to be called by a future
    background job that finds appointments happening soon.
    """

    if not client.email:
        return

    subject = f"Lembrete de agendamento - {business.full_name}"

    body = _appointment_email_body(
        f"Olá {client.full_name}, este é um lembrete do seu agendamento:",
        appointment,
        business,
        service,
        professional,
    )

    email.send_email(client.email, subject, body)
