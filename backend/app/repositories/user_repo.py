# backend/app/repositories/user_repo.py
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models.user import User
from .base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "users", User)

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.get_one({"email": email})

    async def update_refresh_token(self, user_id: str, refresh_token: Optional[str]):
        # We don't store refresh token in this design; we use JWT refresh tokens stateless.
        # This method can be used to store a hashed refresh token if needed.
        pass