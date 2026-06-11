from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.working_hours import WorkingHours
from app.models.user import User

from app.schemas.working_hours import (
    WorkingHoursUpdate,
    WorkingHoursResponse,
)

from app.core.dependencies import (
    get_current_user
)

from app.core.working_hours import get_or_create_working_hours

router = APIRouter(
    prefix="/working-hours",
    tags=["Working Hours"]
)


# DB
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# GET
@router.get("/", response_model=list[WorkingHoursResponse])
def get_working_hours(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_or_create_working_hours(db, current_user.id)


# UPDATE
@router.put("/", response_model=list[WorkingHoursResponse])
def update_working_hours(
    data: WorkingHoursUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    existing = {
        wh.weekday: wh
        for wh in db.query(WorkingHours).filter(
            WorkingHours.owner_id == current_user.id
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
                owner_id=current_user.id,
                weekday=day.weekday,
                start_time=day.start_time,
                end_time=day.end_time,
                is_closed=day.is_closed,
            ))

    db.commit()

    return get_or_create_working_hours(db, current_user.id)
