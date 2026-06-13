import os

from jose import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Define it in a .env file (see .env.example)."
    )

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30
RESET_TOKEN_EXPIRE_MINUTES = 60


def _create_token(data: dict, expires_delta: timedelta, token_type: str | None = None) -> str:

    to_encode = data.copy()

    to_encode["exp"] = datetime.now(timezone.utc) + expires_delta

    if token_type:
        to_encode["type"] = token_type

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def create_access_token(data: dict):
    return _create_token(
        data,
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )


def create_refresh_token(data: dict):
    return _create_token(
        data,
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )


def create_password_reset_token(data: dict):
    return _create_token(
        data,
        timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
        token_type="reset",
    )


def decode_token(token: str) -> dict:
    """Decode a JWT, raising jose.JWTError on failure."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])