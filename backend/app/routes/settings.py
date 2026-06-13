from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.user import User

from app.schemas.settings import SettingsResponse, SettingsUpdate

from app.core.dependencies import get_current_user
from app.core.account import get_account_owner, require_owner

router = APIRouter(
    prefix="/settings",
    tags=["Settings"]
)


# DB
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get("/", response_model=SettingsResponse)
def get_settings(
    account_owner: User = Depends(get_account_owner)
):
    # staff see the settings of the business they belong to
    return account_owner


@router.put("/", response_model=SettingsResponse)
def update_settings(
    data: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):

    user = db.query(User).filter(User.id == current_user.id).first()

    user.monthly_goal = data.monthly_goal
    user.daily_capacity = data.daily_capacity
    user.client_term_singular = data.client_term_singular.strip()
    user.client_term_plural = data.client_term_plural.strip()

    db.commit()
    db.refresh(user)

    return user
