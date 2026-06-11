from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.user import User
from app.models.client import Client
from app.models.service import Service
from app.models.professional import Professional
from app.models.appointment import Appointment
from app.models.review import Review

from app.schemas.public import (
    BusinessInfo,
    PublicServiceResponse,
    PublicProfessionalResponse,
    PublicBookingCreate,
    PublicBookingResponse,
)
from app.schemas.review import ReviewSummary

from app.core.scheduling import compute_available_slots
from app.core.rate_limit import limiter
from app.core.notifications import send_booking_confirmation

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


# PROFESSIONALS
@router.get("/professionals", response_model=list[PublicProfessionalResponse])
def list_public_professionals(
    slug: str,
    db: Session = Depends(get_db)
):

    business = get_business_or_404(slug, db)

    return db.query(Professional).filter(
        Professional.owner_id == business.id,
        Professional.is_active == True,
    ).all()


# REVIEWS
@router.get("/reviews", response_model=ReviewSummary)
def get_public_reviews(
    slug: str,
    db: Session = Depends(get_db)
):

    business = get_business_or_404(slug, db)

    reviews = db.query(Review).filter(
        Review.owner_id == business.id
    ).order_by(Review.created_at.desc()).all()

    total_reviews = len(reviews)

    average_rating = (
        round(sum(r.rating for r in reviews) / total_reviews, 1)
        if total_reviews
        else None
    )

    return {
        "average_rating": average_rating,
        "total_reviews": total_reviews,
        "reviews": reviews[:10],
    }


# AVAILABLE SLOTS
@router.get("/available-slots")
@limiter.limit("60/minute")
def get_public_available_slots(
    request: Request,
    slug: str,
    date: str,
    service_id: int,
    professional_id: int,
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

    professional = db.query(Professional).filter(
        Professional.id == professional_id,
        Professional.owner_id == business.id,
        Professional.is_active == True,
    ).first()

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Professional not found"
        )

    return compute_available_slots(db, business.id, professional_id, service, date)


# CREATE BOOKING
@router.post("/appointments", response_model=PublicBookingResponse)
@limiter.limit("5/minute")
@limiter.limit("30/hour")
def create_public_booking(
    request: Request,
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

    professional = db.query(Professional).filter(
        Professional.id == booking.professional_id,
        Professional.owner_id == business.id,
        Professional.is_active == True,
    ).first()

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Professional not found"
        )

    available_slots = compute_available_slots(
        db,
        business.id,
        professional.id,
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
        professional_id=professional.id,
        scheduled_at=booking.scheduled_at,
        owner_id=business.id,
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    send_booking_confirmation(new_appointment, business, service, professional, client)

    return new_appointment
