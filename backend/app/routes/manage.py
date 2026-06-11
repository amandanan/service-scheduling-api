from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.appointment import Appointment
from app.models.service import Service
from app.models.professional import Professional
from app.models.user import User

from app.schemas.public import (
    ManageAppointmentResponse,
    RescheduleRequest,
)

from app.core.scheduling import compute_available_slots
from app.core.rate_limit import limiter

router = APIRouter(
    prefix="/manage",
    tags=["Manage Booking"]
)


# DB
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def get_appointment_or_404(token: str, db: Session) -> Appointment:
    appointment = db.query(Appointment).filter(
        Appointment.public_token == token
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return appointment


def _to_response(appointment: Appointment, db: Session) -> dict:
    business = db.query(User).filter(User.id == appointment.owner_id).first()
    service = db.query(Service).filter(Service.id == appointment.service_id).first()
    professional = db.query(Professional).filter(
        Professional.id == appointment.professional_id
    ).first()

    return {
        "public_token": appointment.public_token,
        "business_name": business.full_name if business else "",
        "service_name": service.name if service else "",
        "professional_name": professional.name if professional else "",
        "scheduled_at": appointment.scheduled_at,
        "status": appointment.status,
    }


# VIEW
@router.get("/{token}", response_model=ManageAppointmentResponse)
def view_appointment(
    token: str,
    db: Session = Depends(get_db)
):

    appointment = get_appointment_or_404(token, db)

    return _to_response(appointment, db)


# AVAILABLE SLOTS (for rescheduling)
@router.get("/{token}/available-slots")
@limiter.limit("60/minute")
def manage_available_slots(
    request: Request,
    token: str,
    date: str,
    db: Session = Depends(get_db)
):

    appointment = get_appointment_or_404(token, db)

    service = db.query(Service).filter(
        Service.id == appointment.service_id
    ).first()

    return compute_available_slots(
        db,
        appointment.owner_id,
        appointment.professional_id,
        service,
        date,
    )


# CANCEL
@router.post("/{token}/cancel", response_model=ManageAppointmentResponse)
@limiter.limit("10/minute")
def cancel_appointment(
    request: Request,
    token: str,
    db: Session = Depends(get_db)
):

    appointment = get_appointment_or_404(token, db)

    appointment.status = "cancelled"

    db.commit()
    db.refresh(appointment)

    return _to_response(appointment, db)


# RESCHEDULE
@router.post("/{token}/reschedule", response_model=ManageAppointmentResponse)
@limiter.limit("10/minute")
def reschedule_appointment(
    request: Request,
    token: str,
    data: RescheduleRequest,
    db: Session = Depends(get_db)
):

    appointment = get_appointment_or_404(token, db)

    if appointment.status == "cancelled":
        raise HTTPException(
            status_code=409,
            detail="Agendamento cancelado não pode ser remarcado"
        )

    service = db.query(Service).filter(
        Service.id == appointment.service_id
    ).first()

    available_slots = compute_available_slots(
        db,
        appointment.owner_id,
        appointment.professional_id,
        service,
        data.scheduled_at.strftime("%Y-%m-%d"),
    )

    if data.scheduled_at.strftime("%H:%M") not in available_slots:
        raise HTTPException(
            status_code=409,
            detail="Horário indisponível"
        )

    appointment.scheduled_at = data.scheduled_at

    db.commit()
    db.refresh(appointment)

    return _to_response(appointment, db)
