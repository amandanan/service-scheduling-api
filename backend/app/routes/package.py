from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.package import Package, ClientPackage
from app.models.client import Client
from app.models.service import Service
from app.models.user import User

from app.schemas.package import (
    PackageCreate,
    PackageResponse,
    ClientPackagePurchase,
    ClientPackageResponse,
)

from app.core.dependencies import (
    get_current_user
)

router = APIRouter(
    prefix="/packages",
    tags=["Packages"]
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
    response_model=PackageResponse
)
def create_package(
    package: PackageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    service = db.query(Service).filter(
        Service.id == package.service_id,
        Service.owner_id == current_user.id
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    new_package = Package(
        name=package.name,
        service_id=package.service_id,
        total_sessions=package.total_sessions,
        price=package.price,
        owner_id=current_user.id,
    )

    db.add(new_package)

    db.commit()

    db.refresh(new_package)

    return new_package


# LIST
@router.get(
    "/",
    response_model=list[PackageResponse]
)
def list_packages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return db.query(Package).filter(
        Package.owner_id == current_user.id
    ).all()


# UPDATE
@router.put(
    "/{package_id}",
    response_model=PackageResponse
)
def update_package(
    package_id: int,
    package_data: PackageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    package = db.query(Package).filter(
        Package.id == package_id,
        Package.owner_id == current_user.id
    ).first()

    if not package:
        raise HTTPException(
            status_code=404,
            detail="Package not found"
        )

    service = db.query(Service).filter(
        Service.id == package_data.service_id,
        Service.owner_id == current_user.id
    ).first()

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    package.name = package_data.name

    package.service_id = package_data.service_id

    package.total_sessions = package_data.total_sessions

    package.price = package_data.price

    db.commit()

    db.refresh(package)

    return package


# DELETE
@router.delete("/{package_id}")
def delete_package(
    package_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    package = db.query(Package).filter(
        Package.id == package_id,
        Package.owner_id == current_user.id
    ).first()

    if not package:
        raise HTTPException(
            status_code=404,
            detail="Package not found"
        )

    sold = db.query(ClientPackage).filter(
        ClientPackage.package_id == package_id
    ).first()

    if sold:
        raise HTTPException(
            status_code=400,
            detail="Pacote já vendido para clientes e não pode ser excluído"
        )

    db.delete(package)

    db.commit()

    return {
        "message": "Package deleted successfully"
    }


# SELL A PACKAGE TO A CLIENT
@router.post(
    "/purchases",
    response_model=ClientPackageResponse
)
def purchase_package(
    purchase: ClientPackagePurchase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    client = db.query(Client).filter(
        Client.id == purchase.client_id,
        Client.owner_id == current_user.id
    ).first()

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )

    package = db.query(Package).filter(
        Package.id == purchase.package_id,
        Package.owner_id == current_user.id
    ).first()

    if not package:
        raise HTTPException(
            status_code=404,
            detail="Package not found"
        )

    client_package = ClientPackage(
        owner_id=current_user.id,
        client_id=client.id,
        package_id=package.id,
        total_sessions=package.total_sessions,
        remaining_sessions=package.total_sessions,
    )

    db.add(client_package)

    db.commit()

    db.refresh(client_package)

    return client_package


# LIST PURCHASED PACKAGES (BALANCE), OPTIONALLY FILTERED BY CLIENT
@router.get(
    "/purchases",
    response_model=list[ClientPackageResponse]
)
def list_purchases(
    client_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(ClientPackage).filter(
        ClientPackage.owner_id == current_user.id
    )

    if client_id is not None:
        query = query.filter(ClientPackage.client_id == client_id)

    return query.all()
