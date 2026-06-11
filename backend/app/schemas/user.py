from pydantic import BaseModel, EmailStr
from datetime import date


class UserCreate(BaseModel):
    full_name: str
    birth_date: date
    cpf: str
    phone: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    birth_date: date
    cpf: str
    phone: str
    email: EmailStr
    booking_slug: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str