from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.appointment import Appointment
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