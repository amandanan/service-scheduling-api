from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AppointmentBase(BaseModel):

    client_id: int

    service_id: int

    professional_id: int

    scheduled_at: datetime


class AppointmentCreate(
    AppointmentBase
):

    client_package_id: int | None = None


class AppointmentResponse(
    AppointmentBase
):

    id: int

    client_package_id: int | None = None

    model_config = ConfigDict(from_attributes=True)