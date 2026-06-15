import os
import logging
import threading
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.appointment import Appointment
from app.models.user import User
from app.models.service import Service
from app.models.professional import Professional
from app.models.client import Client

from app.core.notifications import send_appointment_reminder

logger = logging.getLogger(__name__)


def send_due_reminders(
    db: Session,
    *,
    hours_before: int = 24,
    now: datetime | None = None,
) -> int:
    """Send a reminder for every upcoming appointment in the window.

    Picks appointments that are not cancelled, happen between ``now`` and
    ``now + hours_before`` and haven't been reminded yet, sends the reminder
    and marks them so it is never sent twice. Returns how many were sent.
    """

    now = now or datetime.now()
    window_end = now + timedelta(hours=hours_before)

    appointments = db.query(Appointment).filter(
        Appointment.status != "cancelled",
        Appointment.reminder_sent_at.is_(None),
        Appointment.scheduled_at > now,
        Appointment.scheduled_at <= window_end,
    ).all()

    sent = 0

    for appointment in appointments:
        business = db.query(User).filter(
            User.id == appointment.owner_id
        ).first()
        service = db.query(Service).filter(
            Service.id == appointment.service_id
        ).first()
        professional = db.query(Professional).filter(
            Professional.id == appointment.professional_id
        ).first()
        client = db.query(Client).filter(
            Client.id == appointment.client_id
        ).first()

        if not (business and service and professional and client):
            continue

        send_appointment_reminder(db, appointment, business, service, professional, client)

        appointment.reminder_sent_at = now
        sent += 1

    if sent:
        db.commit()

    return sent


def run_due_reminders(hours_before: int | None = None) -> int:
    """Open a database session and send due reminders (for cron/jobs)."""

    if hours_before is None:
        hours_before = int(os.getenv("REMINDER_HOURS_BEFORE", "24"))

    db = SessionLocal()

    try:
        return send_due_reminders(db, hours_before=hours_before)

    finally:
        db.close()


# ---- Optional in-process scheduler ----

_stop_event = threading.Event()


def _reminders_enabled() -> bool:
    return os.getenv("REMINDERS_ENABLED", "").strip().lower() in {"1", "true", "yes"}


def start_reminder_scheduler() -> threading.Thread | None:
    """Start a background loop that periodically sends due reminders.

    Disabled unless REMINDERS_ENABLED is truthy, so tests and ad-hoc dev runs
    are unaffected. For multi-instance deployments prefer the cron job
    (python -m app.jobs.send_reminders) to avoid duplicate sends.
    """

    if not _reminders_enabled():
        return None

    interval = int(os.getenv("REMINDER_INTERVAL_MINUTES", "15")) * 60
    hours_before = int(os.getenv("REMINDER_HOURS_BEFORE", "24"))

    _stop_event.clear()

    def loop() -> None:
        while not _stop_event.wait(interval):
            try:
                count = run_due_reminders(hours_before)
                if count:
                    logger.info("Sent %d appointment reminders", count)
            except Exception:
                logger.exception("Reminder job failed")

    thread = threading.Thread(target=loop, daemon=True, name="reminder-scheduler")
    thread.start()

    logger.info("Reminder scheduler started (every %s min)", interval // 60)

    return thread


def stop_reminder_scheduler() -> None:
    _stop_event.set()
