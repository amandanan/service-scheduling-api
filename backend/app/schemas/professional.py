from pydantic import BaseModel, ConfigDict


class ProfessionalCreate(BaseModel):
    name: str
    is_active: bool = True


class ProfessionalUpdate(BaseModel):
    name: str
    is_active: bool = True


class ProfessionalResponse(BaseModel):
    id: int
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
