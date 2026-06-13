from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.service import Service
from app.models.professional import Professional
from app.models.user import User

from app.schemas.service import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
)

from app.core.dependencies import get_current_user
from app.core.account import (
    account_id,
    require_service_writer,
    professional_for_user,
)

router = APIRouter(
    prefix="/services",
    tags=["Services"]
)


# DB
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def _readable_services(db: Session, user: User):
    """Services the user may see: owner/staff see all of the account,
    a professional sees only their own."""
    query = db.query(Service).filter(Service.owner_id == account_id(user))

    if user.role == "professional":
        professional = professional_for_user(db, user)
        professional_id = professional.id if professional else -1
        query = query.filter(Service.professional_id == professional_id)
    elif user.role not in ("owner", "staff"):
        raise HTTPException(status_code=403, detail="Sem permissão")

    return query


def _writable_service_or_404(db: Session, service_id: int, user: User) -> Service:
    """Load a service the user may modify. Owners reach any service in their
    account; professionals only their own. Otherwise 404 (don't leak existence)."""
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.owner_id == account_id(user),
    ).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if user.role == "professional":
        professional = professional_for_user(db, user)
        if professional is None or service.professional_id != professional.id:
            raise HTTPException(status_code=404, detail="Service not found")

    return service


# CREATE
@router.post("/", response_model=ServiceResponse)
def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_service_writer)
):

    professional_id = None

    if current_user.role == "professional":
        # a professional always creates services under themselves
        professional = professional_for_user(db, current_user)
        if professional is None:
            raise HTTPException(status_code=404, detail="Profissional não vinculado")
        professional_id = professional.id

    elif service.professional_id is not None:
        # an owner may assign the service to one of their professionals
        professional = db.query(Professional).filter(
            Professional.id == service.professional_id,
            Professional.owner_id == account_id(current_user),
        ).first()
        if professional is None:
            raise HTTPException(status_code=404, detail="Professional not found")
        professional_id = professional.id

    new_service = Service(
        name=service.name,
        description=service.description,
        price=service.price,
        duration_minutes=service.duration_minutes,
        owner_id=account_id(current_user),
        professional_id=professional_id,
    )

    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    return new_service


# LIST
@router.get("/", response_model=list[ServiceResponse])
def list_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return _readable_services(db, current_user).all()


# GET BY ID
@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = _readable_services(db, current_user).filter(
        Service.id == service_id
    ).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return service


# UPDATE
@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_service_writer)
):
    service = _writable_service_or_404(db, service_id, current_user)

    service.name = service_data.name
    service.description = service_data.description
    service.price = service_data.price
    service.duration_minutes = service_data.duration_minutes
    service.is_active = service_data.is_active

    db.commit()
    db.refresh(service)

    return service


# INACTIVATE (soft delete — keeps appointment history intact)
@router.delete("/{service_id}")
def deactivate_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_service_writer)
):
    service = _writable_service_or_404(db, service_id, current_user)

    service.is_active = False

    db.commit()

    return {"message": "Service deactivated successfully"}
