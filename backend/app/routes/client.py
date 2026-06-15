from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.client import Client
from app.models.user import User

from app.schemas.client import (
    ClientCreate,
    ClientResponse
)

from app.core.account import account_id, require_management

router = APIRouter(
    prefix="/clients",
    tags=["Clients"]
)


# DB
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# CREATE
@router.post("/", response_model=ClientResponse)
def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    duplicate_filters = [Client.email == client.email]
    if client.cpf:
        duplicate_filters.append(Client.cpf == client.cpf)

    existing = db.query(Client).filter(
        Client.owner_id == account_id(current_user),
        or_(*duplicate_filters),
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Cliente já cadastrado com este CPF ou e-mail"
        )

    new_client = Client(
        full_name=client.full_name,
        birth_date=client.birth_date,
        cpf=client.cpf,
        phone=client.phone,
        email=client.email,
        owner_id=account_id(current_user),
        notification_consent=client.notification_consent,
        consent_at=datetime.now() if client.notification_consent else None,
    )

    db.add(new_client)

    db.commit()

    db.refresh(new_client)

    return new_client


# LIST
@router.get("/", response_model=list[ClientResponse])
def list_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    clients = db.query(Client).filter(
        Client.owner_id == account_id(current_user)
    ).all()

    return clients


# GET BY ID
@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    client = db.query(Client).filter(
        Client.id == client_id,
        Client.owner_id == account_id(current_user)
    ).first()

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )

    return client


# DELETE
@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    client = db.query(Client).filter(
        Client.id == client_id,
        Client.owner_id == account_id(current_user)
    ).first()

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )

    db.delete(client)

    db.commit()

    return {
        "message": "Client deleted successfully"
    }


# UPDATE
@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management)
):

    client = db.query(Client).filter(
        Client.id == client_id,
        Client.owner_id == account_id(current_user)
    ).first()

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )

    duplicate_filters = [Client.email == client_data.email]
    if client_data.cpf:
        duplicate_filters.append(Client.cpf == client_data.cpf)

    duplicate = db.query(Client).filter(
        Client.owner_id == account_id(current_user),
        Client.id != client_id,
        or_(*duplicate_filters),
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Cliente já cadastrado com este CPF ou e-mail"
        )

    client.full_name = client_data.full_name
    client.birth_date = client_data.birth_date
    client.cpf = client_data.cpf
    client.phone = client_data.phone
    client.email = client_data.email

    # record the moment consent is (re)granted
    if client_data.notification_consent and not client.notification_consent:
        client.consent_at = datetime.now()
    client.notification_consent = client_data.notification_consent

    db.commit()

    db.refresh(client)

    return client
