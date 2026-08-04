# backend/app/repositories/signal_repo.py
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models.signal import Signal
from .base import BaseRepository

class SignalRepository(BaseRepository[Signal]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "signals", Signal)

    async def get_by_junction(self, junction_id: str) -> Optional[Signal]:
        return await self.get_one({"junction_id": junction_id})