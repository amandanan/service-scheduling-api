from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.dependencies import get_current_user, get_db


def account_id(user: User) -> int:
    """The owner id that scopes a user's data.

    Owners are scoped to themselves; staff members are scoped to the owner
    whose business they belong to. This is the single tenant key used by
    every data query.
    """
    return user.account_owner_id or user.id


def get_account_owner(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Return the account owner User for the current request.

    For an owner this is the user themselves; for staff it is the owner they
    belong to. Used where the owner's row carries account-wide data (settings).
    """
    if current_user.account_owner_id is None:
        return current_user

    owner = db.query(User).filter(
        User.id == current_user.account_owner_id
    ).first()

    if owner is None:
        raise HTTPException(status_code=401, detail="Conta inválida")

    return owner


def require_owner(current_user: User = Depends(get_current_user)) -> User:
    """Allow only account owners (used for staff management and settings)."""
    if current_user.role != "owner":
        raise HTTPException(
            status_code=403,
            detail="Apenas o dono da conta pode realizar esta ação"
        )
    return current_user
