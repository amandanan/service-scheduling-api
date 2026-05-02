from pydantic import BaseModel, EmailStr
from typing import Optional


# Dados que chegam para criar cliente
class ClientCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str


# Dados que chegam para atualizar cliente
class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


# Dados que retornam da API
class ClientResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str

    class Config:
        from_attributes = True
        