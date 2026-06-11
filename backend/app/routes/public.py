from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.user import User
from app.models.client import Client
from app.models.service import Service
from app.models.appointment import Appointment

from app.schemas.public import (
    BusinessInfo,
    PublicServiceResponse,
    PublicBookingCreate,
    PublicBookingResponse,
)

from app.core.scheduling import compute_available_slots

router = APIRouter(
    prefix="/public/{slug}",
    tags=["Public Booking"]
)


# DB
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def get_business_or_404(slug: str, db: Session) -> User:
    business = db.query(User).filter(
        User.booking_slug == slug
    ).first()

    if not business:
        raise HTTPException(
            status_code=404,
            detail="Business not found"
        )

    return business


# BUSINESS INFO
@router.get("/", response_model=BusinessInfo)
def get_business_info(
    slug: str,
    db: Session = Depends(get_db)
):

    return get_business_or_404(slug, db)


# SERVICES
@router.get("/services", response_model=list[PublicServiceResponse])
def list_public_services(
    slug: str,
    db: Session = Depends(get_db)
):

    business = get_business_or_404(slug, db)

    return db.query(Service).filter(
        Service.owner_id == business.id
    ).all()


# AVAILABLE SLOTS
@router.get("/available-slots")
def get_public_available_slots(
    slug: str,
    date: str,
    service_id: int,
    db: Session = Depends(get_db)
):

    business = get_business_or_404(slug, db)

    service = db.query(Service).filter(
        Service.id == service_id,
        Service.owner_id == business.id
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return compute_available_slots(db, business.id, service, date)


# CREATE BOOKING
@router.post("/appointments", response_model=PublicBookingResponse)
def create_public_booking(
    slug: str,
    booking: PublicBookingCreate,
    db: Session = Depends(get_db)
):

    business = get_business_or_404(slug, db)

    service = db.query(Service).filter(
        Service.id == booking.service_id,
        Service.owner_id == business.id
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    available_slots = compute_available_slots(
        db,
        business.id,
        service,
        booking.scheduled_at.strftime("%Y-%m-%d")
    )

    if booking.scheduled_at.strftime("%H:%M") not in available_slots:
        raise HTTPException(
            status_code=409,
            detail="Horário indisponível"
        )

    client = db.query(Client).filter(
        Client.owner_id == business.id,
        Client.cpf == booking.cpf
    ).first()

    if not client:
        client = Client(
            owner_id=business.id,
            full_name=booking.full_name,
            birth_date=booking.birth_date,
            cpf=booking.cpf,
            phone=booking.phone,
            email=booking.email,
        )

        db.add(client)
        db.flush()

    new_appointment = Appointment(
        client_id=client.id,
        service_id=service.id,
        scheduled_at=booking.scheduled_at,
        owner_id=business.id,
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment
