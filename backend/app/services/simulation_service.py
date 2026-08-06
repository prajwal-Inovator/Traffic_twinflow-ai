from typing import List
from datetime import datetime
import os

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.base import BaseRepository
from ..models.simulation_result import SimulationResult
from .http_client import ServiceClient


class SimulationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = BaseRepository(
            db,
            "simulation_results",
            SimulationResult,
        )

        self.simulation_url = os.getenv(
            "SIMULATION_SERVICE_URL",
            "http://localhost:8002",
        )
        self.client = ServiceClient(
            self.simulation_url,
            timeout=120,
            service_name="Simulation Service",
        )

    async def run_simulation(self, params: dict) -> str:
        result = await self.client.request(
            "POST",
            "/simulate",
            json=params,
        )

        simulation_id = result["simulation_id"]

        await self.repo.create(
            {
                "simulation_id": simulation_id,
                "junction_id": params.get("junction_id", "all"),
                "time_horizon": params.get("duration", 30),
                "predicted_congestion": result.get(
                    "predicted_congestion",
                    0,
                ),
                "affected_junctions": result.get(
                    "affected_junctions",
                    [],
                ),
                "propagation_strength": result.get(
                    "propagation_strength",
                    0,
                ),
                "data": result,
                "created_at": datetime.utcnow(),
            }
        )

        return simulation_id

    async def get_ripple_effects(
        self,
        junction_id: str,
        horizons: List[int] | None = None,
    ):
        query = {"junction_id": junction_id}

        if horizons:
            query["time_horizon"] = {"$in": horizons}

        return await self.repo.get_many(
            query,
            limit=100,
            sort=[("created_at", -1)],
        )