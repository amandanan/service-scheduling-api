from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime


class AppointmentBase(BaseModel):

    client_id: int

    service_id: int

    professional_id: int

    scheduled_at: datetime


class AppointmentCreate(
    AppointmentBase
):
    pass


class AppointmentResponse(
    AppointmentBase
):

    id: int

    status: str

    model_config = ConfigDict(from_attributes=True)


# statuses an owner can set after an appointment exists
APPOINTMENT_STATUSES = {"scheduled", "confirmed", "completed", "no_show"}


class AppointmentStatusUpdate(BaseModel):

    status: str

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in APPOINTMENT_STATUSES:
            raise ValueError("Status inválido")
        return value