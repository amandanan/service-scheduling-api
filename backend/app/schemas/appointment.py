from pydantic import BaseModel
from datetime import datetime

from app.schemas.client import ClientResponse
from app.schemas.service import ServiceResponse


class AppointmentBase(BaseModel):
    client_id: int
    service_id: int
    scheduled_at: datetime


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentResponse(BaseModel):
    id: int
    scheduled_at: datetime
    created_at: datetime

    client: ClientResponse
    service: ServiceResponse

    class Config:
        from_attributes = True