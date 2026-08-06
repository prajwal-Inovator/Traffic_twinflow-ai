from typing import Optional

from fastapi import APIRouter, Depends, Query

from ....api.deps import get_db
from ....services.simulation_service import SimulationService

router = APIRouter()


@router.post("/run")
async def run_simulation(
    params: dict,
    db=Depends(get_db),
):
    service = SimulationService(db)

    simulation_id = await service.run_simulation(params)

    return {
        "success": True,
        "data": {
            "simulation_id": simulation_id
        },
    }


@router.get("/ripple/{junction_id}")
async def get_ripple_effects(
    junction_id: str,
    horizons: Optional[str] = Query(
        None,
        description="Comma separated horizons",
    ),
    db=Depends(get_db),
):
    service = SimulationService(db)

    horizon_list = (
        [int(x) for x in horizons.split(",")]
        if horizons
        else None
    )

    result = await service.get_ripple_effects(
        junction_id,
        horizon_list,
    )

    return {
        "success": True,
        "data": result,
    }