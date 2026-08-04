# backend/app/services/auth_service.py
from typing import Optional, Tuple
from datetime import datetime
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from ..core.exceptions import AuthenticationError, ValidationError
from ..repositories.user_repo import UserRepository
from ..models.user import User, UserRole
from ..schemas.auth_schemas import UserCreate, UserLogin, TokenResponse, RefreshTokenRequest
from ..core.redis import get_redis
from ..core.security import decode_token
import time

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_data: UserCreate) -> User:
        # Check if email exists
        existing = await self.user_repo.get_by_email(user_data.email)
        if existing:
            raise ValidationError("Email already registered")

        hashed = get_password_hash(user_data.password)
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["hashed_password"] = hashed
        # Ensure role is valid
        if user_data.role not in UserRole.__members__.values():
            raise ValidationError("Invalid role")

        user = await self.user_repo.create(user_dict)
        return user

    async def authenticate_user(self, email: str, password: str) -> User:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid credentials")
        if not user.is_active:
            raise AuthenticationError("User account is inactive")
        return user

    async def create_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(
            data={"sub": user.id, "role": user.role.value, "email": user.email}
        )
        refresh_token = create_refresh_token(
            data={"sub": user.id}
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=30 * 60,  # 30 minutes
            user=user,
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        # Create new token pair (rotate)
        access_token = create_access_token(
            data={"sub": user.id, "role": user.role.value, "email": user.email}
        )
        new_refresh = create_refresh_token(data={"sub": user.id})
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
            token_type="bearer",
            expires_in=30 * 60,
            user=user,
        )
    async def blacklist_token(self, token: str, expires_in: int = 30 * 60) -> bool:
        """Add token to Redis blacklist with expiry."""
        redis = await get_redis()
        # Use the token's jti (or a hash) as key
        # For simplicity, we store the token itself with TTL
        # In production, store a hash or use the token's exp claim.
        payload = decode_token(token)
        if not payload:
            return False
        exp = payload.get("exp")
        if exp:
            ttl = max(0, exp - int(time.time()))
        else:
            ttl = expires_in
        key = f"bl:token:{token[:20]}"  # use a prefix and first 20 chars
        await redis.setex(key, ttl, "revoked")
        return True

    async def is_token_blacklisted(self, token: str) -> bool:
        redis = await get_redis()
        key = f"bl:token:{token[:20]}"
        return await redis.exists(key) == 1

    async def revoke_refresh_token(self, refresh_token: str) -> bool:
        # We can blacklist refresh tokens as well
        return await self.blacklist_token(refresh_token, expires_in=7 * 24 * 60 * 60)

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        # First check if the refresh token is blacklisted
        if await self.is_token_blacklisted(refresh_token):
            raise AuthenticationError("Refresh token revoked")

        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        # Blacklist the old refresh token (rotation)
        await self.revoke_refresh_token(refresh_token)

        # Create new token pair
        access_token = create_access_token(
            data={"sub": user.id, "role": user.role.value, "email": user.email}
        )
        new_refresh = create_refresh_token(data={"sub": user.id})
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
            token_type="bearer",
            expires_in=30 * 60,
            user=user,
        )

    async def logout(self, access_token: str) -> bool:
        return await self.blacklist_token(access_token)
