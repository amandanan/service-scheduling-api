from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.user import User

from app.schemas.staff import StaffCreate, StaffResponse

from app.core.account import require_owner
from app.routes.auth import hash_password

router = APIRouter(
    prefix="/staff",
    tags=["Staff"]
)


# DB
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# CREATE a staff member under the current owner's account
@router.post("/", response_model=StaffResponse)
def create_staff(
    staff: StaffCreate,
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner)
):

    existing = db.query(User).filter(User.email == staff.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="E-mail já cadastrado"
        )

    existing_cpf = db.query(User).filter(User.cpf == staff.cpf).first()
    if existing_cpf:
        raise HTTPException(
            status_code=400,
            detail="CPF já cadastrado"
        )

    member = User(
        full_name=staff.full_name,
        birth_date=staff.birth_date,
        cpf=staff.cpf,
        phone=staff.phone,
        email=staff.email,
        hashed_password=hash_password(staff.password),
        booking_slug=None,
        account_owner_id=owner.id,
        role="staff",
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


# LIST staff of the current owner's account
@router.get("/", response_model=list[StaffResponse])
def list_staff(
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner)
):

    return db.query(User).filter(
        User.account_owner_id == owner.id
    ).order_by(User.full_name).all()


# DELETE a staff member from the account
@router.delete("/{staff_id}")
def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner)
):

    member = db.query(User).filter(
        User.id == staff_id,
        User.account_owner_id == owner.id,
    ).first()

    if not member:
        raise HTTPException(
            status_code=404,
            detail="Staff member not found"
        )

    db.delete(member)
    db.commit()

    return {"message": "Staff member deleted successfully"}
