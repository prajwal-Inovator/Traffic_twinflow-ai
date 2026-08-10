# simulation/main.py
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from sumo_wrapper import SUMOWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
sim = SUMOWrapper(config_file="/app/sumo_config.sumocfg")

@app.on_event("startup")
async def startup():
    async def _start_sumo():
        loop = asyncio.get_running_loop()
        started = await loop.run_in_executor(None, sim.start)
        if not started:
            logger.warning("SUMO failed to start; the API remains available.")

    asyncio.create_task(_start_sumo())

@app.on_event("shutdown")
async def shutdown():
    sim.stop()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/simulation/step")
async def step(steps: int = 1):
    try:
        sim.step(steps)
        return {"simulation_time": sim.simulation_time}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

@app.get("/simulation/vehicles")
async def get_vehicles():
    return sim.get_vehicle_positions()

@app.get("/simulation/traffic_lights")
async def get_traffic_lights():
    return sim.get_traffic_light_states()

@app.get("/simulation/detectors")
async def get_detectors():
    return sim.get_detector_data()