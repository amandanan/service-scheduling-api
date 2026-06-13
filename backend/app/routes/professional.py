from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.professional import Professional
from app.models.working_hours import WorkingHours
from app.models.user import User

from app.schemas.professional import (
    ProfessionalCreate,
    ProfessionalUpdate,
    ProfessionalResponse,
)
from app.schemas.working_hours import (
    WorkingHoursUpdate,
    WorkingHoursResponse,
)

from app.core.dependencies import get_current_user
from app.core.working_hours import get_or_create_working_hours

router = APIRouter(
    prefix="/professionals",
    tags=["Professionals"]
)
from app.core.account import account_id


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
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
):

    return db.query(Professional).filter(
        Professional.owner_id == account_id(current_user)
    ).all()


# UPDATE
@router.put("/{professional_id}", response_model=ProfessionalResponse)
def update_professional(
    professional_id: int,
    data: ProfessionalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
):

    professional = get_professional_or_404(db, professional_id, account_id(current_user))

    db.delete(professional)
    db.commit()

    return {"message": "Professional deleted successfully"}


# WORKING HOURS
@router.get(
    "/{professional_id}/working-hours",
    response_model=list[WorkingHoursResponse]
)
def get_working_hours(
    professional_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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
