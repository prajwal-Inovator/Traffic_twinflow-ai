from fastapi import Depends, HTTPException, status

from ..core.database import get_db
from ..repositories.user_repo import UserRepository
from ..services.auth_service import AuthService


def get_auth_service(db=Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


async def get_current_user(
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Temporary authentication dependency.

    Replace this later with JWT validation.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not implemented.",
    )


async def get_current_active_user(
    current_user=Depends(get_current_user),
):
    return current_user