from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date


class ClientCreate(BaseModel):
    full_name: str
    birth_date: date
    cpf: str
    phone: str
    email: EmailStr


class ClientResponse(BaseModel):
    id: int
    full_name: str
    birth_date: date
    cpf: str
    phone: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
        