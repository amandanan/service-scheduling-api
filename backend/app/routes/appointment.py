from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.appointment import Appointment
from app.models.client import Client
from app.models.service import Service
from app.models.user import User

from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse
)

from app.core.dependencies import (
    get_current_user
)

from app.core.scheduling import compute_available_slots

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

    if appointment.scheduled_at <= datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Não é possível agendar em uma data passada"
        )

    client = db.query(Client).filter(
        Client.id == appointment.client_id,
        Client.owner_id == current_user.id
    ).first()

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )

    service = db.query(Service).filter(
        Service.id == appointment.service_id,
        Service.owner_id == current_user.id
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    new_appointment = Appointment(

        client_id=appointment.client_id,

        service_id=appointment.service_id,

        scheduled_at=appointment.scheduled_at,

        owner_id=current_user.id
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
    ).filter(
        Appointment.owner_id == current_user.id
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
        Service.id == service_id,
        Service.owner_id == current_user.id
    ).first()

    if not service:

        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return compute_available_slots(db, current_user.id, service, date)


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
        Appointment.id == appointment_id,
        Appointment.owner_id == current_user.id
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
        Appointment.id == appointment_id,
        Appointment.owner_id == current_user.id
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

    if appointment_data.scheduled_at <= datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Não é possível agendar em uma data passada"
        )

    appointment = db.query(
        Appointment
    ).filter(
        Appointment.id == appointment_id,
        Appointment.owner_id == current_user.id
    ).first()

    if not appointment:

        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    client = db.query(Client).filter(
        Client.id == appointment_data.client_id,
        Client.owner_id == current_user.id
    ).first()

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )

    service = db.query(Service).filter(
        Service.id == appointment_data.service_id,
        Service.owner_id == current_user.id
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
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