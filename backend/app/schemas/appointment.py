from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AppointmentBase(BaseModel):

    client_id: int

    service_id: int

    scheduled_at: datetime


class AppointmentCreate(
    AppointmentBase
):
    pass


class AppointmentResponse(
    AppointmentBase
):

    id: int

    model_config = ConfigDict(from_attributes=True)