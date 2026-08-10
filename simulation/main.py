import logging
from fastapi import FastAPI, HTTPException
from sumo_wrapper import SUMOWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

sim = SUMOWrapper(config_file="/app/sumo_config.sumocfg")


# ✅ ROOT (Render health fix)
@app.get("/")
def root():
    return {"message": "TwinFlow Simulation Running"}


# ✅ HEALTH
@app.get("/health")
def health():
    return {"status": "ok"}


# ✅ START SIMULATION (ON DEMAND)
@app.get("/start")
def start():
    if not sim.is_running:
        sim.start()
    return {"status": "started"}


# ✅ STEP SIMULATION (SAFE)
@app.get("/step")
def step(steps: int = 1):
    try:
        if not sim.is_running:
            sim.start()

        sim.step(steps)
        return {"simulation_time": sim.simulation_time}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ GET VEHICLES
@app.get("/vehicles")
def vehicles():
    if not sim.is_running:
        return {"message": "simulation not started"}
    return sim.get_vehicle_positions()


# ✅ TRAFFIC LIGHTS
@app.get("/traffic")
def traffic():
    if not sim.is_running:
        return {}
    return sim.get_traffic_light_states()


# ✅ STOP (VERY IMPORTANT FOR MEMORY)
@app.get("/stop")
def stop():
    sim.stop()
    return {"status": "stopped"}