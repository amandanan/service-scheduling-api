from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.service import Service

from app.core.working_hours import get_or_create_working_hours


def compute_available_slots(db: Session, owner_id: int, professional_id: int, service: Service, date: str) -> list[str]:
    duration = service.duration_minutes or 60

    requested_date = datetime.strptime(date, "%Y-%m-%d")

    now = datetime.now()

    # don't offer slots for days that already passed
    if requested_date.date() < now.date():
        return []

    working_hours_by_weekday = {
        wh.weekday: wh
        for wh in get_or_create_working_hours(db, professional_id)
    }

    working_hours = working_hours_by_weekday[requested_date.weekday()]

    if working_hours.is_closed:
        return []

    day_start = datetime.combine(requested_date.date(), working_hours.start_time)
    day_end = datetime.combine(requested_date.date(), working_hours.end_time)

    appointments = db.query(Appointment).filter(
        Appointment.professional_id == professional_id,
        Appointment.status != "cancelled",
    ).all()

    services_by_id = {
        s.id: s
        for s in db.query(Service).filter(Service.owner_id == owner_id).all()
    }

    available_slots = []
    current = day_start

    while current < day_end:

        # skip slots that already started (relevant when booking for today)
        if current <= now:
            current += timedelta(minutes=30)
            continue

        current_end = current + timedelta(minutes=duration)

        has_conflict = False

        for appointment in appointments:

            appointment_service = services_by_id.get(appointment.service_id)

            appointment_duration = (
                appointment_service.duration_minutes
                if appointment_service and appointment_service.duration_minutes
                else 60
            )

            appointment_end = appointment.scheduled_at + timedelta(minutes=appointment_duration)

            conflict = (
                current < appointment_end
                and current_end > appointment.scheduled_at
            )

            if conflict:
                has_conflict = True
                break

        if not has_conflict:
            available_slots.append(current.strftime("%H:%M"))

        current += timedelta(minutes=30)

    return available_slots
