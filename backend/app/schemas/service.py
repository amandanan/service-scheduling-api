from pydantic import BaseModel, ConfigDict


class ServiceBase(BaseModel):

    name: str

    price: float

    duration_minutes: int


class ServiceCreate(ServiceBase):
    pass


class ServiceResponse(ServiceBase):

    id: int

    model_config = ConfigDict(from_attributes=True)