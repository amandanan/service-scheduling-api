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
from app.models.professional import Professional
from app.models.user import User

from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentStatusUpdate,
)

from app.core.account import account_id, require_management

from app.core.scheduling import compute_available_slots
from app.core.notifications import send_booking_confirmation

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
    current_user: User = Depends(require_management)
):

    if appointment.scheduled_at <= datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Não é possível agendar em uma data passada"
        )

    client = db.query(Client).filter(
        Client.id == appointment.client_id,
        Client.owner_id == account_id(current_user)
    ).first()

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )

    service = db.query(Service).filter(
        Service.id == appointment.service_id,
        Service.owner_id == account_id(current_user)
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    professional = db.query(Professional).filter(
        Professional.id == appointment.professional_id,
        Professional.owner_id == account_id(current_user)
    ).first()

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Professional not found"
        )

    new_appointment = Appointment(

        client_id=appointment.client_id,

        service_id=appointment.service_id,

        professional_id=appointment.professional_id,

        scheduled_at=appointment.scheduled_at,

        owner_id=account_id(current_user),
    )

    db.add(new_appointment)

    db.commit()

    db.refresh(new_appointment)

    send_booking_confirmation(new_appointment, current_user, service, professional, client)

    return new_appointment


# LIST
@router.get(
    "/",
    response_model=list[AppointmentResponse]
)
def list_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    appointments = db.query(
        Appointment
    ).filter(
        Appointment.owner_id == account_id(current_user),
        Appointment.status != "cancelled",
    ).all()

    return appointments


# AVAILABLE SLOTS
@router.get("/available-slots")
def get_available_slots(
    date: str,
    service_id: int,
    professional_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    service = db.query(Service).filter(
        Service.id == service_id,
        Service.owner_id == account_id(current_user)
    ).first()

    if not service:

        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    professional = db.query(Professional).filter(
        Professional.id == professional_id,
        Professional.owner_id == account_id(current_user)
    ).first()

    if not professional:

        raise HTTPException(
            status_code=404,
            detail="Professional not found"
        )

    return compute_available_slots(db, account_id(current_user), professional_id, service, date)


# GET BY ID
@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    appointment = db.query(
        Appointment
    ).filter(
        Appointment.id == appointment_id,
        Appointment.owner_id == account_id(current_user)
    ).first()

    if not appointment:

        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return appointment


# UPDATE STATUS (mark completed / no-show / confirmed)
@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentResponse
)
def update_appointment_status(
    appointment_id: int,
    data: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.owner_id == account_id(current_user)
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    if appointment.status == "cancelled":
        raise HTTPException(
            status_code=409,
            detail="Agendamento cancelado não pode mudar de status"
        )

    appointment.status = data.status

    db.commit()
    db.refresh(appointment)

    return appointment


# DELETE
@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    appointment = db.query(
        Appointment
    ).filter(
        Appointment.id == appointment_id,
        Appointment.owner_id == account_id(current_user)
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
    current_user: User = Depends(require_management)
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
        Appointment.owner_id == account_id(current_user)
    ).first()

    if not appointment:

        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    client = db.query(Client).filter(
        Client.id == appointment_data.client_id,
        Client.owner_id == account_id(current_user)
    ).first()

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )

    service = db.query(Service).filter(
        Service.id == appointment_data.service_id,
        Service.owner_id == account_id(current_user)
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    professional = db.query(Professional).filter(
        Professional.id == appointment_data.professional_id,
        Professional.owner_id == account_id(current_user)
    ).first()

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Professional not found"
        )

    appointment.client_id = (
        appointment_data.client_id
    )

    appointment.service_id = (
        appointment_data.service_id
    )

    appointment.professional_id = (
        appointment_data.professional_id
    )

    appointment.scheduled_at = (
        appointment_data.scheduled_at
    )

    db.commit()

    db.refresh(appointment)

    return appointment