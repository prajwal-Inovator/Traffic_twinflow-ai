# simulation/sumo_wrapper.py
import os
import sys
import subprocess
import time
import logging
import traci
import traci.constants as tc
from typing import List, Dict, Any, Optional, Tuple
import xml.etree.ElementTree as ET
import threading
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class SUMOWrapper:
    """Asynchronous wrapper for SUMO simulation using TraCI."""

    def __init__(
        self,
        sumo_binary: str = "sumo",
        config_file: str = "sumo_config.sumocfg",
        gui: bool = False,
        headless: bool = True,
    ):
        self.sumo_binary = "sumo-gui" if gui else sumo_binary
        self.config_file = config_file
        self.headless = headless
        self.process = None
        self.is_running = False
        self.simulation_time = 0
        self.vehicles = {}
        self.traffic_light_states = {}
        self.detector_data = {}
        self.lock = threading.Lock()

    def start(self, **kwargs) -> bool:
        """Start the SUMO simulation process."""
        if self.is_running:
            logger.warning("SUMO is already running.")
            return False

        try:
            cmd = [
                self.sumo_binary,
                "-c", self.config_file,
                "--start",
                "--quit-on-end",
                "--no-warnings",
            ]
            if self.headless:
                cmd.append("--no-gui")

            # Add additional arguments
            for key, value in kwargs.items():
                cmd.append(f"--{key}")
                cmd.append(str(value))

            logger.info(f"Starting SUMO with command: {' '.join(cmd)}")
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Connect to TraCI
            traci.connect(port=8813, numRetries=10, wait=0.5)
            self.is_running = True
            self.simulation_time = 0
            logger.info("SUMO started and TraCI connected.")
            return True

        except Exception as e:
            logger.error(f"Failed to start SUMO: {e}")
            return False

    def step(self, steps: int = 1) -> float:
        """Advance simulation by a number of steps (seconds)."""
        if not self.is_running:
            raise RuntimeError("SUMO is not running.")
        for _ in range(steps):
            traci.simulationStep()
            self.simulation_time += 1
        return self.simulation_time

    def stop(self):
        """Stop the simulation and close TraCI."""
        if self.is_running:
            traci.close()
            self.is_running = False
            if self.process:
                self.process.terminate()
                self.process = None
            logger.info("SUMO stopped.")

    def get_vehicle_positions(self) -> List[Dict[str, Any]]:
        """Get current positions and data for all vehicles."""
        vehicle_ids = traci.vehicle.getIDList()
        vehicles = []
        for vid in vehicle_ids:
            try:
                pos = traci.vehicle.getPosition(vid)
                speed = traci.vehicle.getSpeed(vid)
                angle = traci.vehicle.getAngle(vid)
                vehicle_type = traci.vehicle.getVehicleClass(vid)
                lane = traci.vehicle.getLaneIndex(vid)
                edge = traci.vehicle.getRoadID(vid)
                vehicles.append({
                    "id": vid,
                    "x": pos[0],
                    "y": pos[1],
                    "speed": speed,
                    "angle": angle,
                    "type": vehicle_type,
                    "lane": lane,
                    "edge": edge,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                })
            except traci.TraCIException:
                # Vehicle may have left the simulation
                continue
        return vehicles

    def get_traffic_light_states(self) -> Dict[str, str]:
        """Get current state of all traffic lights."""
        tls_ids = traci.trafficlight.getIDList()
        states = {}
        for tls_id in tls_ids:
            state = traci.trafficlight.getRedYellowGreenState(tls_id)
            states[tls_id] = state
        return states

    def set_traffic_light_state(self, tls_id: str, state: str):
        """Set traffic light state (e.g., 'GGGG', 'rrrr')."""
        if self.is_running:
            traci.trafficlight.setRedYellowGreenState(tls_id, state)

    def get_detector_data(self, detector_id: str) -> Dict[str, Any]:
        """Get data from an induction loop detector."""
        if not self.is_running:
            return {}
        # Use traci.inductionloop methods
        last_vehicle = traci.inductionloop.getLastStepVehicleNumber(detector_id)
        occupancy = traci.inductionloop.getLastStepOccupancy(detector_id)
        speed = traci.inductionloop.getLastStepMeanSpeed(detector_id)
        return {
            "vehicle_count": last_vehicle,
            "occupancy": occupancy,
            "mean_speed": speed,
            "timestamp": self.simulation_time,
        }

    def add_vehicle(self, vehicle_id: str, route_id: str, depart: float = 0.0, **kwargs):
        """Add a vehicle to the simulation."""
        if self.is_running:
            traci.vehicle.add(vehicle_id, route_id, depart=depart, **kwargs)

    def add_route(self, route_id: str, edges: List[str]):
        """Add a route to the simulation."""
        if self.is_running:
            traci.route.add(route_id, edges)

    def get_edge_occupancy(self, edge_id: str) -> float:
        """Get occupancy of an edge (fraction)."""
        if self.is_running:
            return traci.edge.getLastStepOccupancy(edge_id)
        return 0.0

    def get_edge_vehicle_count(self, edge_id: str) -> int:
        """Get number of vehicles on an edge."""
        if self.is_running:
            return traci.edge.getLastStepVehicleNumber(edge_id)
        return 0

    def run_simulation(self, duration: int, callback=None) -> Dict[str, Any]:
        """Run simulation for a given duration (seconds), optionally calling callback each step."""
        if not self.is_running:
            if not self.start():
                return {"error": "Could not start SUMO."}
        try:
            for _ in range(duration):
                self.step()
                if callback:
                    callback(self)
            return {
                "status": "completed",
                "simulation_time": self.simulation_time,
                "vehicle_count": len(traci.vehicle.getIDList()),
                "last_step": duration,
            }
        except Exception as e:
            logger.error(f"Simulation error: {e}")
            return {"error": str(e)}
        finally:
            self.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()