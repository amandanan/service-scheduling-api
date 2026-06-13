from pydantic import BaseModel, ConfigDict, Field


class ServiceBase(BaseModel):

    name: str

    description: str | None = None

    price: float = Field(ge=0)

    duration_minutes: int = Field(gt=0)


class ServiceCreate(ServiceBase):

    # only honoured for admins; a professional always creates under themselves
    professional_id: int | None = None


class ServiceUpdate(ServiceBase):

    is_active: bool = True


class ServiceResponse(ServiceBase):

    id: int

    is_active: bool

    professional_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
