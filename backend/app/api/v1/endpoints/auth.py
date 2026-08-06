from fastapi import APIRouter, Depends, status

from ....api.deps import (
    get_db,
    get_current_user,
)
from ....repositories.user_repo import UserRepository
from ....services.auth_service import AuthService
from ....schemas.auth_schemas import (
    UserCreate,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
)
from ....models.user import User

router = APIRouter()


def get_auth_service(db=Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.register_user(user_data)
    return await auth_service.create_tokens(user)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.authenticate_user(
        login_data.email,
        login_data.password,
    )
    return await auth_service.create_tokens(user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.refresh_access_token(
        refresh_data.refresh_token
    )


@router.get(
    "/me",
    response_model=User,
)
async def me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
):
    # Stateless JWT logout.
    # If token blacklisting is enabled later,
    # implement it inside AuthService.
    return {
        "success": True,
        "message": "Logged out successfully",
    }