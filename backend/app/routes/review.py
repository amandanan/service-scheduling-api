from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.review import Review
from app.models.user import User

from app.schemas.review import OwnerReviewResponse

from app.core.account import account_id, require_management

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


# DB
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# LIST
@router.get(
    "/",
    response_model=list[OwnerReviewResponse]
)
def list_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    return db.query(Review).filter(
        Review.owner_id == account_id(current_user)
    ).order_by(Review.created_at.desc()).all()
