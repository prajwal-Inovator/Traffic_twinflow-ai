# simulation/async_sumo_wrapper.py
import asyncio
import concurrent.futures
import threading
from typing import Callable, Optional, Dict, Any
from .sumo_wrapper import SUMOWrapper
import logging

logger = logging.getLogger(__name__)

class AsyncSUMO:
    """Asynchronous interface to SUMO running in a thread."""

    def __init__(self, config_file: str = "sumo_config.sumocfg", gui: bool = False):
        self.config_file = config_file
        self.gui = gui
        self.wrapper = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.loop = asyncio.get_event_loop()

    async def start(self) -> bool:
        """Start SUMO asynchronously."""
        def _start():
            self.wrapper = SUMOWrapper(config_file=self.config_file, gui=self.gui)
            return self.wrapper.start()

        return await self.loop.run_in_executor(self.executor, _start)

    async def stop(self):
        """Stop SUMO asynchronously."""
        if self.wrapper:
            def _stop():
                self.wrapper.stop()
            await self.loop.run_in_executor(self.executor, _stop)

    async def step(self, steps: int = 1) -> float:
        """Advance simulation."""
        if not self.wrapper:
            raise RuntimeError("SUMO not started.")
        def _step():
            return self.wrapper.step(steps)
        return await self.loop.run_in_executor(self.executor, _step)

    async def get_vehicle_positions(self) -> list:
        """Get vehicles asynchronously."""
        if not self.wrapper:
            return []
        def _get():
            return self.wrapper.get_vehicle_positions()
        return await self.loop.run_in_executor(self.executor, _get)

    async def get_traffic_light_states(self) -> dict:
        """Get traffic light states."""
        if not self.wrapper:
            return {}
        def _get():
            return self.wrapper.get_traffic_light_states()
        return await self.loop.run_in_executor(self.executor, _get)

    async def set_traffic_light_state(self, tls_id: str, state: str):
        """Set traffic light state."""
        if self.wrapper:
            def _set():
                self.wrapper.set_traffic_light_state(tls_id, state)
            await self.loop.run_in_executor(self.executor, _set)

    async def run_simulation(self, duration: int) -> Dict[str, Any]:
        """Run simulation for specified duration."""
        if not self.wrapper:
            await self.start()
        def _run():
            return self.wrapper.run_simulation(duration)
        return await self.loop.run_in_executor(self.executor, _run)

    async def add_vehicle(self, vehicle_id: str, route_id: str, depart: float = 0.0, **kwargs):
        """Add a vehicle."""
        if self.wrapper:
            def _add():
                self.wrapper.add_vehicle(vehicle_id, route_id, depart, **kwargs)
            await self.loop.run_in_executor(self.executor, _add)

    async def add_route(self, route_id: str, edges: list):
        """Add a route."""
        if self.wrapper:
            def _add():
                self.wrapper.add_route(route_id, edges)
            await self.loop.run_in_executor(self.executor, _add)