# simulation/main.py

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from sumo_wrapper import SUMOWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize SUMO
sim = SUMOWrapper(config_file="/app/sumo_config.sumocfg")


# ✅ Startup: run SUMO in background (non-blocking)
@app.on_event("startup")
async def startup():
    async def _start_sumo():
        loop = asyncio.get_running_loop()
        started = await loop.run_in_executor(None, sim.start)
        if not started:
            logger.warning("SUMO failed to start; API still running.")

    asyncio.create_task(_start_sumo())


# ✅ Shutdown
@app.on_event("shutdown")
async def shutdown():
    sim.stop()


# ✅ ROOT ENDPOINT (fixes Render "In Progress")
@app.get("/")
async def root():
    return {"message": "TwinFlow Simulation Running"}


# ✅ HEALTH CHECK
@app.get("/health")
async def health():
    return {"status": "ok"}


# ✅ SIMULATION STEP
@app.get("/simulation/step")
async def step(steps: int = 1):
    try:
        sim.step(steps)
        return {"simulation_time": sim.simulation_time}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


# ✅ VEHICLE DATA
@app.get("/simulation/vehicles")
async def get_vehicles():
    return sim.get_vehicle_positions()


# ✅ TRAFFIC LIGHT DATA
@app.get("/simulation/traffic-lights")
async def get_traffic_lights():
    return sim.get_traffic_light_states()


# ✅ DETECTOR DATA (safe fallback)
@app.get("/simulation/detectors")
async def get_detectors():
    try:
        # Example detector ID (change if needed)
        return sim.get_detector_data("detector_1")
    except Exception:
        return {"message": "No detector data available"}