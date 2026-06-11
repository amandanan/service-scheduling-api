import re
import secrets

from sqlalchemy.orm import Session

from app.models.user import User


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "loja"


def generate_unique_booking_slug(db: Session, full_name: str) -> str:
    base_slug = slugify(full_name)
    slug = base_slug

    while db.query(User).filter(User.booking_slug == slug).first():
        slug = f"{base_slug}-{secrets.token_hex(2)}"

    return slug
