# backend/app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, status
from ....api.deps import get_db, get_current_user
from ....core.database import get_db as get_db_dep
from ....repositories.user_repo import UserRepository
from ....services.auth_service import AuthService
from ....schemas.auth_schemas import UserCreate, UserLogin, TokenResponse, RefreshTokenRequest
from ....models.user import User

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    access_token: str = Depends(security)
):
    """Logout – blacklist the current access token."""
    service = AuthService(UserRepository(db))  # need db
    # We need to pass db – we'll use Depends
    # Better: restructure to get service from Depends
    result = await service.logout(access_token.credentials)
    return {"success": result, "message": "Logged out successfully"}

# To use dependency injection for AuthService, we can create a dependency:
def get_auth_service(db=Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))

# Then in endpoints:
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    tokens = await auth_service.refresh_access_token(refresh_data.refresh_token)
    return tokens
    
router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db=Depends(get_db)):
    repo = UserRepository(db)
    service = AuthService(repo)
    user = await service.register_user(user_data)
    tokens = await service.create_tokens(user)
    return tokens

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db=Depends(get_db)):
    repo = UserRepository(db)
    service = AuthService(repo)
    user = await service.authenticate_user(login_data.email, login_data.password)
    tokens = await service.create_tokens(user)
    return tokens

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db=Depends(get_db)):
    repo = UserRepository(db)
    service = AuthService(repo)
    tokens = await service.refresh_access_token(refresh_data.refresh_token)
    return tokens

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    # JWT is stateless; client should discard token
    # Optionally add token to a blacklist (Redis) here
    return {"success": True, "message": "Logged out successfully"}