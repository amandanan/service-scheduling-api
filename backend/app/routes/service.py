from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.service import Service
from app.models.user import User

from app.schemas.service import (
    ServiceCreate,
    ServiceResponse
)

from app.core.dependencies import (
    get_current_user
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


# CREATE
@router.post(
    "/",
    response_model=ServiceResponse
)
def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    new_service = Service(

        name=service.name,

        price=service.price,

        duration_minutes=
            service.duration_minutes,

        owner_id=current_user.id
    )

    db.add(new_service)

    db.commit()

    db.refresh(new_service)

    return new_service


# LIST
@router.get(
    "/",
    response_model=list[ServiceResponse]
)
def list_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    services = db.query(Service).filter(
        Service.owner_id == current_user.id
    ).all()

    return services


# GET BY ID
@router.get(
    "/{service_id}",
    response_model=ServiceResponse
)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    service = db.query(Service).filter(
        Service.id == service_id,
        Service.owner_id == current_user.id
    ).first()

    if not service:

        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return service


# DELETE
@router.delete("/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    service = db.query(Service).filter(
        Service.id == service_id,
        Service.owner_id == current_user.id
    ).first()

    if not service:

        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    db.delete(service)

    db.commit()

    return {
        "message":
            "Service deleted successfully"
    }


# UPDATE
@router.put(
    "/{service_id}",
    response_model=ServiceResponse
)
def update_service(
    service_id: int,
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    service = db.query(Service).filter(
        Service.id == service_id,
        Service.owner_id == current_user.id
    ).first()

    if not service:

        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    service.name = service_data.name

    service.price = service_data.price

    service.duration_minutes = (
        service_data.duration_minutes
    )

    db.commit()

    db.refresh(service)

    return service