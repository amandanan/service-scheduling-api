from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.time_block import TimeBlock
from app.models.professional import Professional
from app.models.user import User

from app.schemas.time_block import TimeBlockCreate, TimeBlockResponse

from app.core.account import account_id, require_management

router = APIRouter(
    prefix="/blocks",
    tags=["Time Blocks"]
)


# DB
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# CREATE
@router.post("/", response_model=TimeBlockResponse)
def create_block(
    block: TimeBlockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    professional = db.query(Professional).filter(
        Professional.id == block.professional_id,
        Professional.owner_id == account_id(current_user),
    ).first()

    if not professional:
        raise HTTPException(
            status_code=404,
            detail="Professional not found"
        )

    new_block = TimeBlock(
        owner_id=account_id(current_user),
        professional_id=block.professional_id,
        start_at=block.start_at,
        end_at=block.end_at,
        reason=block.reason,
    )

    db.add(new_block)
    db.commit()
    db.refresh(new_block)

    return new_block


# LIST (optionally filtered by professional)
@router.get("/", response_model=list[TimeBlockResponse])
def list_blocks(
    professional_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    query = db.query(TimeBlock).filter(
        TimeBlock.owner_id == account_id(current_user)
    )

    if professional_id is not None:
        query = query.filter(TimeBlock.professional_id == professional_id)

    return query.order_by(TimeBlock.start_at).all()


# DELETE
@router.delete("/{block_id}")
def delete_block(
    block_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    block = db.query(TimeBlock).filter(
        TimeBlock.id == block_id,
        TimeBlock.owner_id == account_id(current_user),
    ).first()

    if not block:
        raise HTTPException(
            status_code=404,
            detail="Block not found"
        )

    db.delete(block)
    db.commit()

    return {"message": "Block deleted successfully"}
