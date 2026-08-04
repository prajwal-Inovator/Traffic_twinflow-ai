# backend/app/services/analytics_service.py
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..repositories.base import BaseRepository
from ..models.vehicle import Vehicle
from ..models.incident import Incident
from ..models.simulation_result import SimulationResult
from datetime import datetime, timedelta

class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.vehicle_repo = BaseRepository[Vehicle](db, "vehicles", Vehicle)
        self.incident_repo = BaseRepository[Incident](db, "incidents", Incident)
        self.sim_repo = BaseRepository[SimulationResult](db, "simulation_results", SimulationResult)

    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Aggregate key metrics for dashboard."""
        # Placeholder: we'll just return dummy data
        vehicle_count = len(await self.vehicle_repo.get_many({}, limit=100))
        incident_count = len(await self.incident_repo.get_many({"resolved": False}, limit=50))
        return {
            "total_vehicles": vehicle_count,
            "active_incidents": incident_count,
            "average_speed": 35.2,
            "co2_saved_today": 120.5,
        }