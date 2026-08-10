# simulation/sumo_wrapper.py

import subprocess
import logging
import traci
import threading
from typing import List, Dict, Any
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
        self.is_running = False
        self.simulation_time = 0
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

            # ✅ Correct way (NO connect())
            traci.start(cmd)

            self.is_running = True
            self.simulation_time = 0

            logger.info("SUMO started successfully with TraCI.")
            return True

        except Exception as e:
            logger.error(f"Failed to start SUMO: {e}")
            self.is_running = False
            return False

    def step(self, steps: int = 1) -> float:
        """Advance simulation by steps."""
        if not self.is_running:
            raise RuntimeError("SUMO is not running.")

        for _ in range(steps):
            traci.simulationStep()
            self.simulation_time += 1

        return self.simulation_time

    def stop(self):
        """Stop the simulation."""
        if self.is_running:
            try:
                traci.close()
            except Exception:
                pass

            self.is_running = False
            logger.info("SUMO stopped.")

    def get_vehicle_positions(self) -> List[Dict[str, Any]]:
        vehicles = []
        try:
            vehicle_ids = traci.vehicle.getIDList()
        except Exception:
            return vehicles

        for vid in vehicle_ids:
            try:
                pos = traci.vehicle.getPosition(vid)
                vehicles.append({
                    "id": vid,
                    "x": pos[0],
                    "y": pos[1],
                    "speed": traci.vehicle.getSpeed(vid),
                    "angle": traci.vehicle.getAngle(vid),
                    "type": traci.vehicle.getVehicleClass(vid),
                    "lane": traci.vehicle.getLaneIndex(vid),
                    "edge": traci.vehicle.getRoadID(vid),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                })
            except Exception:
                continue

        return vehicles

    def get_traffic_light_states(self) -> Dict[str, str]:
        states = {}
        try:
            tls_ids = traci.trafficlight.getIDList()
        except Exception:
            return states

        for tls_id in tls_ids:
            states[tls_id] = traci.trafficlight.getRedYellowGreenState(tls_id)

        return states

    def set_traffic_light_state(self, tls_id: str, state: str):
        if self.is_running:
            try:
                traci.trafficlight.setRedYellowGreenState(tls_id, state)
            except Exception:
                pass

    def run_simulation(self, duration: int, callback=None) -> Dict[str, Any]:
        """Run simulation safely."""
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