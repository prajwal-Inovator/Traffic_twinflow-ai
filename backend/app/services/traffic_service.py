# backend/app/services/traffic_service.py
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..repositories.vehicle_repo import VehicleRepository
from ..repositories.signal_repo import SignalRepository
from ..repositories.base import BaseRepository
from ..models.vehicle import Vehicle
from ..models.signal import Signal
from ..models.incident import Incident
from ..core.exceptions import NotFoundError

class TrafficService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.vehicle_repo = VehicleRepository(db)
        self.signal_repo = SignalRepository(db)
        self.incident_repo = BaseRepository[Incident](db, "incidents", Incident)

    async def get_live_traffic(self) -> dict:
        """Fetch latest vehicles, signals, and incidents."""
        vehicles = await self.vehicle_repo.get_recent(minutes=5, limit=1000)
        signals = await self.signal_repo.get_many({}, limit=100)
        incidents = await self.incident_repo.get_many({"resolved": False}, limit=50)
        return {
            "vehicles": vehicles,
            "signals": signals,
            "incidents": incidents,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    async def get_vehicles_by_junction(self, junction_id: str) -> List[Vehicle]:
        return await self.vehicle_repo.get_by_junction(junction_id)

    async def create_incident(self, incident_data: dict) -> Incident:
        return await self.incident_repo.create(incident_data)

    async def resolve_incident(self, incident_id: str) -> Incident:
        incident = await self.incident_repo.update(incident_id, {"resolved": True, "end_time": datetime.utcnow()})
        if not incident:
            raise NotFoundError("Incident not found")
        return incident

from datetime import datetime