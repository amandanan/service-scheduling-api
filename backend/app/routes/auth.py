from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm

from app.database.session import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.security import create_access_token


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# utils
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# REGISTER
@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email já cadastrado"
        )

    hashed_password = hash_password(user.password)

    db_user = User(
        full_name=user.full_name,
        birth_date=user.birth_date,
        cpf=user.cpf,
        phone=user.phone,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# LOGIN
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if (
        not db_user
        or not verify_password(
            form_data.password,
            db_user.hashed_password
        )
    ):
        raise HTTPException(
            status_code=400,
            detail="Credenciais inválidas"
        )

    token = create_access_token({
        "sub": db_user.email
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }