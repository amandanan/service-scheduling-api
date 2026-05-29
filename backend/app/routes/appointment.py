from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from datetime import (
    datetime,
    timedelta,
)

from app.database.session import SessionLocal

from app.models.appointment import Appointment
from app.models.service import Service
from app.models.user import User

from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse
)

from app.core.dependencies import (
    get_current_user
)

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


# DB
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# CREATE
@router.post(
    "/",
    response_model=AppointmentResponse
)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    new_appointment = Appointment(

        client_id=appointment.client_id,

        service_id=appointment.service_id,

        scheduled_at=appointment.scheduled_at
    )

    db.add(new_appointment)

    db.commit()

    db.refresh(new_appointment)

    return new_appointment


# LIST
@router.get(
    "/",
    response_model=list[AppointmentResponse]
)
def list_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    appointments = db.query(
        Appointment
    ).all()

    return appointments


# AVAILABLE SLOTS
@router.get("/available-slots")
def get_available_slots(
    date: str,
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    service = db.query(Service).filter(
        Service.id == service_id
    ).first()

    if not service:

        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    duration = (
        service.duration_minutes or 60
    )

    day_start = datetime.strptime(
        f"{date} 08:00",
        "%Y-%m-%d %H:%M"
    )

    day_end = datetime.strptime(
        f"{date} 20:00",
        "%Y-%m-%d %H:%M"
    )

    appointments = db.query(
        Appointment
    ).all()

    available_slots = []

    current = day_start

    while current < day_end:

        current_end = (
            current +
            timedelta(minutes=duration)
        )

        has_conflict = False

        for appointment in appointments:

            appointment_service = db.query(
                Service
            ).filter(
                Service.id ==
                appointment.service_id
            ).first()

            appointment_duration = (
                appointment_service.duration_minutes
                if appointment_service
                and appointment_service.duration_minutes
                else 60
            )

            appointment_end = (
                appointment.scheduled_at +
                timedelta(
                    minutes=appointment_duration
                )
            )

            conflict = (

                current < appointment_end

                and

                current_end >
                appointment.scheduled_at
            )

            if conflict:

                has_conflict = True

                break

        if not has_conflict:

            available_slots.append(
                current.strftime("%H:%M")
            )

        current += timedelta(minutes=30)

    return available_slots


# GET BY ID
@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    appointment = db.query(
        Appointment
    ).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:

        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return appointment


# DELETE
@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    appointment = db.query(
        Appointment
    ).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:

        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    db.delete(appointment)

    db.commit()

    return {
        "message":
        "Appointment deleted successfully"
    }


# UPDATE
@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    appointment = db.query(
        Appointment
    ).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:

        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    appointment.client_id = (
        appointment_data.client_id
    )

    appointment.service_id = (
        appointment_data.service_id
    )

    appointment.scheduled_at = (
        appointment_data.scheduled_at
    )

    db.commit()

    db.refresh(appointment)

    return appointment