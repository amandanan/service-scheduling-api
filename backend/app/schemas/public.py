from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import date, datetime

from app.core.cpf import validate_and_normalize_cpf


class BusinessInfo(BaseModel):
    full_name: str
    booking_slug: str

    model_config = ConfigDict(from_attributes=True)


class PublicServiceResponse(BaseModel):
    id: int
    name: str
    price: float
    duration_minutes: int

    model_config = ConfigDict(from_attributes=True)


class PublicBookingCreate(BaseModel):
    full_name: str
    birth_date: date
    cpf: str
    phone: str
    email: EmailStr
    service_id: int
    scheduled_at: datetime

    @field_validator("cpf")
    @classmethod
    def _validate_cpf(cls, value: str) -> str:
        return validate_and_normalize_cpf(value)


class PublicBookingResponse(BaseModel):
    id: int
    service_id: int
    scheduled_at: datetime

    model_config = ConfigDict(from_attributes=True)
