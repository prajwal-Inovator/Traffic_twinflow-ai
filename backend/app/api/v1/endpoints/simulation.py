# backend/app/api/v1/endpoints/simulation.py
from fastapi import APIRouter, Depends, Query
from ....api.deps import get_db
from ....services.simulation_service import SimulationService
from typing import List, Optional
from fastapi import APIRouter, Depends, BackgroundTasks
from ....services.simulation_service import SimulationService
from ....core.database import get_db
import logging
from ....simulation.async_sumo_wrapper import AsyncSUMO

router = APIRouter()
logger = logging.getLogger(__name__)

# Global instance (could be per request, but we'll keep a singleton)
# In production, use a connection pool.
sumo_instance = None

@router.post("/run")
async def run_simulation(
    params: dict,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    """Run a SUMO simulation asynchronously."""
    global sumo_instance
    if sumo_instance is None:
        sumo_instance = AsyncSUMO(config_file="simulation/sumo_config.sumocfg")
        await sumo_instance.start()

    # Run simulation in background
    duration = params.get("duration", 300)
    background_tasks.add_task(_run_simulation_task, sumo_instance, duration, db)
    return {"success": True, "message": "Simulation started in background."}

async def _run_simulation_task(sumo, duration, db):
    try:
        result = await sumo.run_simulation(duration)
        # Save results to MongoDB
        service = SimulationService(db)
        await service.save_simulation_result(result)
        logger.info(f"Simulation completed: {result}")
    except Exception as e:
        logger.error(f"Simulation task failed: {e}")

router = APIRouter()

@router.post("/run")
async def run_simulation(params: dict, db=Depends(get_db)):
    service = SimulationService(db)
    sim_id = await service.run_simulation(params)
    return {"success": True, "data": {"simulation_id": sim_id}}

@router.get("/ripple/{junction_id}")
async def get_ripple_effects(
    junction_id: str,
    horizons: Optional[str] = Query(None, description="Comma-separated horizons (5,10,20,30)"),
    db=Depends(get_db)
):
    service = SimulationService(db)
    horizon_list = [int(h) for h in horizons.split(",")] if horizons else None
    effects = await service.get_ripple_effects(junction_id, horizon_list)
    return {"success": True, "data": effects}

@router.post("/ripple/simulate")
async def run_ripple_simulation(
    data: dict,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    junction_id = data.get("junction_id")
    congestion = data.get("congestion", 80.0)
    if not junction_id:
        return {"success": False, "error": "junction_id required"}
    service = SimulationService(db)
    # Run in background to avoid blocking
    background_tasks.add_task(service.simulate_ripple, junction_id, congestion)
    return {"success": True, "message": "Ripple simulation started in background."}