# backend/app/repositories/vehicle_repo.py
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models.vehicle import Vehicle
from .base import BaseRepository

class VehicleRepository(BaseRepository[Vehicle]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "vehicles", Vehicle)

    async def get_by_junction(self, junction_id: str, limit: int = 100) -> List[Vehicle]:
        return await self.get_many({"junction_id": junction_id}, limit=limit)

    async def get_recent(self, minutes: int = 5, limit: int = 1000) -> List[Vehicle]:
        # This would need a timestamp filter; we'll leave as placeholder
        return await self.get_many({}, limit=limit)