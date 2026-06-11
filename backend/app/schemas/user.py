from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import date

from app.core.cpf import validate_and_normalize_cpf


class UserCreate(BaseModel):
    full_name: str
    birth_date: date
    cpf: str
    phone: str
    email: EmailStr
    password: str

    @field_validator("cpf")
    @classmethod
    def _validate_cpf(cls, value: str) -> str:
        return validate_and_normalize_cpf(value)


class UserResponse(BaseModel):
    id: int
    full_name: str
    birth_date: date
    cpf: str
    phone: str
    email: EmailStr
    booking_slug: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str