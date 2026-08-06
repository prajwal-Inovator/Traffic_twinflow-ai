from functools import lru_cache

from fastapi import Depends, HTTPException, status
from jose import JWTError

from ..core.database import get_db
from ..repositories.user_repo import UserRepository
from ..services.auth_service import AuthService
from digital_twin import TwinEngine


@lru_cache()
def get_twin_engine() -> TwinEngine:
    """Singleton TwinEngine instance."""
    return TwinEngine(config_path="digital_twin/config.yaml")


def get_auth_service(db=Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


async def get_current_user(
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Temporary dependency.

    Replace this implementation with your JWT validation logic if your
    AuthService exposes one.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="get_current_user() is not implemented.",
    )


async def get_current_active_user(
    current_user=Depends(get_current_user),
):
    return current_user