from pydantic import BaseModel


class ServiceBase(BaseModel):

    name: str

    price: float

    duration_minutes: int


class ServiceCreate(ServiceBase):
    pass


class ServiceResponse(ServiceBase):

    id: int

    class Config:
        from_attributes = True