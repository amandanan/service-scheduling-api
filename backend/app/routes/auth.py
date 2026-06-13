from jose import JWTError

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm

from app.database.session import SessionLocal
from app.models.user import User
from app.models.professional import Professional
from app.schemas.user import (
    UserCreate,
    UserResponse,
    Token,
    AccessToken,
    RefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    decode_token,
)
from app.core.slugs import generate_unique_booking_slug
from app.core.dependencies import get_current_user
from app.core.notifications import send_password_reset


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
        hashed_password=hashed_password,
        booking_slug=generate_unique_booking_slug(db, user.full_name)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # every business starts with a default professional so the
    # scheduling flow works out of the box
    default_professional = Professional(
        owner_id=db_user.id,
        name=user.full_name,
        is_active=True,
    )

    db.add(default_professional)
    db.commit()

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

    return {
        "access_token": create_access_token({"sub": db_user.email}),
        "refresh_token": create_refresh_token({"sub": db_user.email}),
        "token_type": "bearer"
    }


# REFRESH ACCESS TOKEN
@router.post("/refresh", response_model=AccessToken)
def refresh(
    data: RefreshRequest,
    db: Session = Depends(get_db)
):

    invalid = HTTPException(
        status_code=401,
        detail="Refresh token inválido"
    )

    try:
        payload = decode_token(data.refresh_token)
    except JWTError:
        raise invalid

    if payload.get("type") != "refresh":
        raise invalid

    email = payload.get("sub")

    if not email:
        raise invalid

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise invalid

    return {
        "access_token": create_access_token({"sub": user.email}),
        "token_type": "bearer"
    }


# FORGOT PASSWORD
@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == data.email).first()

    # only send when the account exists, but always answer the same way so
    # the endpoint can't be used to discover which e-mails are registered
    if user:
        reset_token = create_password_reset_token({"sub": user.email})
        send_password_reset(user, reset_token)

    return {
        "message": "Se o e-mail estiver cadastrado, enviaremos um link de redefinição."
    }


# RESET PASSWORD
@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    invalid = HTTPException(
        status_code=400,
        detail="Link de redefinição inválido ou expirado"
    )

    try:
        payload = decode_token(data.token)
    except JWTError:
        raise invalid

    if payload.get("type") != "reset":
        raise invalid

    email = payload.get("sub")

    if not email:
        raise invalid

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise invalid

    user.hashed_password = hash_password(data.new_password)

    db.commit()

    return {
        "message": "Senha redefinida com sucesso"
    }


# CURRENT USER
@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):

    return current_user