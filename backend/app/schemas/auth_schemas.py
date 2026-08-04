# backend/app/schemas/auth_schemas.py
from pydantic import BaseModel, EmailStr
from ..models.user import User, UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User

class RefreshTokenRequest(BaseModel):
    refresh_token: str