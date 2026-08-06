from typing import List
from datetime import datetime
import os

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.base import BaseRepository
from ..models.simulation_result import SimulationResult


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

    async def run_simulation(self, params: dict) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.simulation_url}/simulate",
                json=params,
            )

        response.raise_for_status()

        result = response.json()

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