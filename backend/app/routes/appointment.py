from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database.session import SessionLocal
from app.models.appointment import Appointment
from app.models.client import Client
from app.models.service import Service
from app.schemas.appointment import AppointmentCreate, AppointmentResponse

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
router = APIRouter(prefix="/appointments", tags=["Appointments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE
@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)  # rota protegida
):
    client = db.query(Client).filter(Client.id == appointment.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    service = db.query(Service).filter(Service.id == appointment.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    new_start = appointment.scheduled_at
    new_end = new_start + timedelta(minutes=service.duration)

    existing_appointments = db.query(Appointment).all()
    services_dict = {s.id: s.duration for s in db.query(Service).all()}  # otimização

    for existing in existing_appointments:
        existing_start = existing.scheduled_at
        existing_end = existing_start + timedelta(minutes=services_dict[existing.service_id])

        if new_start < existing_end and new_end > existing_start:
            raise HTTPException(
                status_code=400,
                detail="Time slot conflicts with another appointment"
            )

    new_appointment = Appointment(
        client_id=appointment.client_id,
        service_id=appointment.service_id,
        scheduled_at=appointment.scheduled_at
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment


# LIST
@router.get("/", response_model=list[AppointmentResponse])
def list_appointments(db: Session = Depends(get_db)):
    return db.query(Appointment).all()


# GET BY ID
@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):

    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return appointment


# DELETE
@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):

    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db.delete(appointment)
    db.commit()

    return {"message": "Appointment deleted successfully"}