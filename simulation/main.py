# simulation/main.py
import asyncio
import logging
from fastapi import FastAPI, BackgroundTasks
from .sumo_wrapper import SUMOWrapper
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
sim = SUMOWrapper()

@app.on_event("startup")
async def startup():
    sim.start()

@app.on_event("shutdown")
async def shutdown():
    sim.stop()

@app.get("/simulation/step")
async def step(steps: int = 1):
    sim.step(steps)
    return {"simulation_time": sim.simulation_time}

@app.get("/simulation/vehicles")
async def get_vehicles():
    return sim.get_vehicle_data()

@app.get("/simulation/traffic_lights")
async def get_traffic_lights():
    return sim.get_traffic_light_data()

@app.get("/simulation/detectors")
async def get_detectors():
    return sim.get_detector_data()