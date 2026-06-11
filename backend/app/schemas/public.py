from pydantic import BaseModel, EmailStr
from datetime import date, datetime


class BusinessInfo(BaseModel):
    full_name: str
    booking_slug: str

    class Config:
        from_attributes = True


class PublicServiceResponse(BaseModel):
    id: int
    name: str
    price: float
    duration_minutes: int

    class Config:
        from_attributes = True


class PublicBookingCreate(BaseModel):
    full_name: str
    birth_date: date
    cpf: str
    phone: str
    email: EmailStr
    service_id: int
    scheduled_at: datetime


class PublicBookingResponse(BaseModel):
    id: int
    service_id: int
    scheduled_at: datetime

    class Config:
        from_attributes = True
