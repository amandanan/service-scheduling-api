from datetime import date

from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

from app.core.cpf import validate_and_normalize_cpf


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
    user_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ProfessionalLoginCreate(BaseModel):
    """Identity data to provision a login for an existing professional."""
    email: EmailStr
    password: str = Field(min_length=6)
    cpf: str
    phone: str
    birth_date: date

    @field_validator("cpf")
    @classmethod
    def _validate_cpf(cls, value: str) -> str:
        return validate_and_normalize_cpf(value)
