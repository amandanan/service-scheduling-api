from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.professional import Professional
from app.models.working_hours import WorkingHours
from app.models.appointment import Appointment
from app.models.user import User

from app.schemas.professional import (
    ProfessionalCreate,
    ProfessionalUpdate,
    ProfessionalResponse,
    ProfessionalLoginCreate,
)
from app.schemas.working_hours import (
    WorkingHoursUpdate,
    WorkingHoursResponse,
)
from app.schemas.appointment import AppointmentResponse

from app.core.working_hours import get_or_create_working_hours
from app.core.account import account_id, require_management, get_current_professional
from app.routes.auth import hash_password

router = APIRouter(
    prefix="/professionals",
    tags=["Professionals"]
)


# DB
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def get_professional_or_404(db: Session, professional_id: int, owner_id: int) -> Professional:
    professional = db.query(Professional).filter(
        Professional.id == professional_id,
        Professional.owner_id == owner_id,
    ).first()

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Professional not found"
        )

    return professional


# CREATE
@router.post("/", response_model=ProfessionalResponse)
def create_professional(
    professional: ProfessionalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    new_professional = Professional(
        owner_id=account_id(current_user),
        name=professional.name,
        is_active=professional.is_active,
    )

    db.add(new_professional)
    db.commit()
    db.refresh(new_professional)

    return new_professional


# LIST
@router.get("/", response_model=list[ProfessionalResponse])
def list_professionals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    return db.query(Professional).filter(
        Professional.owner_id == account_id(current_user)
    ).all()


# --- Professional self-service (role="professional") ---

# MY PROFILE
@router.get("/me", response_model=ProfessionalResponse)
def get_my_professional(
    professional: Professional = Depends(get_current_professional)
):
    return professional


# MY AGENDA (read-only)
@router.get("/me/appointments", response_model=list[AppointmentResponse])
def get_my_appointments(
    db: Session = Depends(get_db),
    professional: Professional = Depends(get_current_professional)
):
    return db.query(Appointment).filter(
        Appointment.professional_id == professional.id,
        Appointment.status != "cancelled",
    ).order_by(Appointment.scheduled_at).all()


# UPDATE
@router.put("/{professional_id}", response_model=ProfessionalResponse)
def update_professional(
    professional_id: int,
    data: ProfessionalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    professional = get_professional_or_404(db, professional_id, account_id(current_user))

    professional.name = data.name
    professional.is_active = data.is_active

    db.commit()
    db.refresh(professional)

    return professional


# DELETE
@router.delete("/{professional_id}")
def delete_professional(
    professional_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    professional = get_professional_or_404(db, professional_id, account_id(current_user))

    db.delete(professional)
    db.commit()

    return {"message": "Professional deleted successfully"}


# PROVISION LOGIN for an existing professional (admin/staff)
@router.post("/{professional_id}/login", response_model=ProfessionalResponse)
def create_professional_login(
    professional_id: int,
    data: ProfessionalLoginCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    professional = get_professional_or_404(db, professional_id, account_id(current_user))

    if professional.user_id is not None:
        raise HTTPException(
            status_code=409,
            detail="Este profissional já possui acesso"
        )

    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    if db.query(User).filter(User.cpf == data.cpf).first():
        raise HTTPException(status_code=400, detail="CPF já cadastrado")

    user = User(
        full_name=professional.name,
        birth_date=data.birth_date,
        cpf=data.cpf,
        phone=data.phone,
        email=data.email,
        hashed_password=hash_password(data.password),
        booking_slug=None,
        account_owner_id=account_id(current_user),
        role="professional",
    )

    db.add(user)
    db.flush()

    professional.user_id = user.id

    db.commit()
    db.refresh(professional)

    return professional


# WORKING HOURS
@router.get(
    "/{professional_id}/working-hours",
    response_model=list[WorkingHoursResponse]
)
def get_working_hours(
    professional_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    get_professional_or_404(db, professional_id, account_id(current_user))

    return get_or_create_working_hours(db, professional_id)


@router.put(
    "/{professional_id}/working-hours",
    response_model=list[WorkingHoursResponse]
)
def update_working_hours(
    professional_id: int,
    data: WorkingHoursUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    get_professional_or_404(db, professional_id, account_id(current_user))

    existing = {
        wh.weekday: wh
        for wh in db.query(WorkingHours).filter(
            WorkingHours.professional_id == professional_id
        ).all()
    }

    for day in data.days:

        entry = existing.get(day.weekday)

        if entry:
            entry.start_time = day.start_time
            entry.end_time = day.end_time
            entry.is_closed = day.is_closed

        else:
            db.add(WorkingHours(
                professional_id=professional_id,
                weekday=day.weekday,
                start_time=day.start_time,
                end_time=day.end_time,
                is_closed=day.is_closed,
            ))

    db.commit()

    return get_or_create_working_hours(db, professional_id)
