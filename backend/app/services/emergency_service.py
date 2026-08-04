# backend/app/services/emergency_service.py
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..repositories.base import BaseRepository
from ..models.incident import Incident
from ..models.signal import Signal
from ..core.exceptions import NotFoundError

class EmergencyService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.incident_repo = BaseRepository[Incident](db, "incidents", Incident)
        self.signal_repo = BaseRepository[Signal](db, "signals", Signal)

    async def get_active_emergencies(self) -> List[Incident]:
        return await self.incident_repo.get_many({
            "resolved": False,
            "severity": {"$in": ["high", "critical"]}
        }, limit=20)

    async def create_emergency_corridor(self, incident_id: str) -> dict:
        """Activate emergency corridor by adjusting signals."""
        # Placeholder: override signals along a path
        return {"status": "activated", "incident_id": incident_id}

    async def resolve_emergency(self, incident_id: str) -> Incident:
        return await self.incident_repo.update(incident_id, {"resolved": True, "end_time": datetime.utcnow()})

from datetime import datetime