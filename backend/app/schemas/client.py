from pydantic import BaseModel, EmailStr
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

    class Config:
        from_attributes = True
        