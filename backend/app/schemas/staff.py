from datetime import date

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

from app.core.cpf import validate_and_normalize_cpf


class StaffCreate(BaseModel):
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


class StaffResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    role: str

    model_config = ConfigDict(from_attributes=True)
