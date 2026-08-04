# backend/app/services/simulation_service.py
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..repositories.base import BaseRepository
from ..models.simulation_result import SimulationResult
from ..core.exceptions import NotFoundError
from ....simulation.sumo_wrapper import SUMOWrapper
from ai.ripple.ripple_simulator import RippleSimulator
from ai.ripple.propagation_model import PropagationModel
        
class SimulationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = BaseRepository[SimulationResult](db, "simulation_results", SimulationResult)

    async def run_simulation(self, params: dict) -> str:
        """Trigger a SUMO simulation (placeholder)."""
        # In later steps we integrate SUMO
        simulation_id = f"sim_{datetime.utcnow().timestamp()}"
        # Store a record
        await self.repo.create({
            "simulation_id": simulation_id,
            "junction_id": params.get("junction_id", "all"),
            "time_horizon": params.get("duration", 30),
            "predicted_congestion": 0.0,
            "affected_junctions": [],
            "propagation_strength": 0.0,
            "data": params,
        })
        return simulation_id

     async def get_ripple_effects(self, junction_id: str, horizons: List[int] = None) -> List[SimulationResult]:
        """Retrieve stored ripple effects."""
        filter = {"junction_id": junction_id}
        if horizons:
            filter["time_horizon"] = {"$in": horizons}
        return await self.repo.get_many(filter, limit=100, sort=[("created_at", -1)])   
    
    async def load_network(self):
        """Load road network from the database into the ripple simulator."""
        # Fetch junctions (signals) and roads from DB
        signal_repo = BaseRepository(db, "signals", Signal)
        road_repo = BaseRepository(db, "roads", RoadSegment)

        junctions = await signal_repo.get_many({})
        roads = await road_repo.get_many({})

        junction_list = [{"id": j.junction_id, "lat": j.lat, "lng": j.lng} for j in junctions]
        road_list = [
            {
                "start_junction_id": r.start_junction_id,
                "end_junction_id": r.end_junction_id,
                "length": r.length,
                "speed_limit": r.speed_limit,
                "lanes": r.lanes,
            } for r in roads
        ]
        self.ripple_simulator.load_network(junction_list, road_list)
    
    async def simulate_ripple(self, junction_id: str, congestion: float = 80.0) -> Dict:
        """Run ripple simulation and store result."""
        # Ensure network is loaded
        if not self.ripple_simulator.model.graph:
            await self.load_network()

        result = await self.ripple_simulator.simulate_ripple_async(junction_id, congestion)
        # Store in DB
        for horizon, data in result["horizons"].items():
            sim_result = {
                "simulation_id": f"ripple_{junction_id}_{datetime.utcnow().timestamp()}",
                "junction_id": junction_id,
                "time_horizon": int(horizon),
                "predicted_congestion": data["max_strength"] * 100,  # scale
                "affected_junctions": list(data["affected_junctions"].keys()),
                "propagation_strength": data["max_strength"],
                "data": data,
                "created_at": datetime.utcnow(),
            }
            await self.repo.create(sim_result)

        return result
