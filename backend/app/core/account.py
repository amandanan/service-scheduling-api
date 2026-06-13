from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.professional import Professional
from app.core.dependencies import get_current_user, get_db

# roles allowed to run business/management operations
MANAGEMENT_ROLES = ("owner", "staff")


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


def require_management(current_user: User = Depends(get_current_user)) -> User:
    """Allow business management roles (admin/owner and staff).

    Professionals and clients are scoped to their own data and use dedicated
    endpoints instead of the account-wide management routes.
    """
    if current_user.role not in MANAGEMENT_ROLES:
        raise HTTPException(
            status_code=403,
            detail="Acesso restrito à administração do negócio"
        )
    return current_user


def professional_for_user(db: Session, user: User) -> Professional | None:
    """The Professional linked to a user, or None if they aren't one."""
    return db.query(Professional).filter(
        Professional.user_id == user.id
    ).first()


def require_service_writer(current_user: User = Depends(get_current_user)) -> User:
    """Only the owner (any service) or a professional (their own) may write
    services. Receptionists/staff manage clients and appointments, not the
    service catalog."""
    if current_user.role not in ("owner", "professional"):
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para gerenciar serviços"
        )
    return current_user


def get_current_professional(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Professional:
    """Return the Professional linked to the signed-in professional user."""
    if current_user.role != "professional":
        raise HTTPException(
            status_code=403,
            detail="Disponível apenas para profissionais"
        )

    professional = db.query(Professional).filter(
        Professional.user_id == current_user.id
    ).first()

    if professional is None:
        raise HTTPException(
            status_code=404,
            detail="Profissional não vinculado a este usuário"
        )

    return professional
