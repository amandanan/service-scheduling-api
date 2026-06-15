from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import date, datetime

from app.core.cpf import validate_and_normalize_cpf
from app.schemas.review import ReviewResponse


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


class PublicProfessionalResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class PublicBookingCreate(BaseModel):
    full_name: str
    birth_date: date
    cpf: str | None = None
    phone: str
    email: EmailStr
    service_id: int
    professional_id: int
    scheduled_at: datetime
    notification_consent: bool = True

    @field_validator("cpf")
    @classmethod
    def _validate_cpf(cls, value: str | None) -> str | None:
        if value is None or value.strip() == "":
            return None
        return validate_and_normalize_cpf(value)


class PublicBookingResponse(BaseModel):
    id: int
    service_id: int
    professional_id: int
    scheduled_at: datetime
    public_token: str

    model_config = ConfigDict(from_attributes=True)


class ManageAppointmentResponse(BaseModel):
    public_token: str
    business_name: str
    service_name: str
    professional_name: str
    scheduled_at: datetime
    status: str
    can_review: bool
    can_confirm: bool
    can_cancel: bool
    review: ReviewResponse | None = None


class RescheduleRequest(BaseModel):
    scheduled_at: datetime
