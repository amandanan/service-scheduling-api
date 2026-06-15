from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import date

from app.core.cpf import validate_and_normalize_cpf


class ClientCreate(BaseModel):
    full_name: str
    birth_date: date
    cpf: str | None = None
    phone: str
    email: EmailStr
    notification_consent: bool = True

    @field_validator("cpf")
    @classmethod
    def _validate_cpf(cls, value: str | None) -> str | None:
        if value is None or value.strip() == "":
            return None
        return validate_and_normalize_cpf(value)


class ClientResponse(BaseModel):
    id: int
    full_name: str
    birth_date: date
    cpf: str | None
    phone: str
    email: EmailStr
    notification_consent: bool

    model_config = ConfigDict(from_attributes=True)
        