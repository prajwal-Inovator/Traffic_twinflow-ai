# digital_twin/data_sync.py
import asyncio
import logging
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import random
import aiohttp
from ..backend.app.repositories.vehicle_repo import VehicleRepository
from ..backend.app.repositories.signal_repo import SignalRepository
from ..backend.app.repositories.base import BaseRepository
from ..backend.app.models.vehicle import Vehicle
from ..backend.app.models.signal import Signal
from ..backend.app.models.incident import Incident
import yaml

logger = logging.getLogger(__name__)

class DataSync:
    """Synchronize live data from external sources (or simulate) into the twin."""

    def __init__(self, db: AsyncIOMotorDatabase, config_path: str = "config.yaml"):
        self.db = db
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.vehicle_repo = VehicleRepository(db)
        self.signal_repo = SignalRepository(db)
        self.incident_repo = BaseRepository[Incident](db, "incidents", Incident)

        self.is_running = False
        self.sync_task = None

    async def start(self):
        """Start the sync loop."""
        self.is_running = True
        self.sync_task = asyncio.create_task(self._sync_loop())
        logger.info("Data sync started")

    async def _sync_loop(self):
        while self.is_running:
            try:
                await self.sync_live_data()
            except Exception as e:
                logger.error(f"Data sync error: {e}")
            await asyncio.sleep(self.config.get("update_interval", 5))

    async def sync_live_data(self):
        """Fetch live traffic data from external APIs or simulate, and store in DB."""
        # Placeholder: we simulate traffic data
        # In production, we would fetch from real APIs (e.g., OpenWeather, Tavily)
        await self._simulate_vehicles()
        await self._simulate_signals()
        await self._simulate_incidents()

    async def _simulate_vehicles(self):
        """Generate synthetic vehicle data (for demo)."""
        # Generate random vehicles around a center point
        center_lat = 28.6139
        center_lng = 77.2090
        for _ in range(20):
            lat = center_lat + random.uniform(-0.01, 0.01)
            lng = center_lng + random.uniform(-0.01, 0.01)
            vehicle_data = {
                "external_id": f"veh_{random.randint(1000,9999)}",
                "type": random.choice(["car", "bus", "truck", "motorcycle"]),
                "speed": random.uniform(10, 60),
                "heading": random.uniform(0, 360),
                "lat": lat,
                "lng": lng,
                "junction_id": f"node_{random.randint(1, 100)}",
                "lane": random.randint(0, 2),
                "timestamp": datetime.utcnow(),
            }
            await self.vehicle_repo.create(vehicle_data)

    async def _simulate_signals(self):
        """Update signal phases for junctions."""
        # For simplicity, we assume we have signals in DB; we can update phases randomly
        signals = await self.signal_repo.get_many({}, limit=10)
        for signal in signals:
            new_phase = random.choice(["red", "yellow", "green"])
            await self.signal_repo.update(
                signal.id,
                {"phase": new_phase, "timestamp": datetime.utcnow()}
            )

    async def _simulate_incidents(self):
        """Generate random incidents."""
        if random.random() < 0.1:  # 10% chance of new incident per cycle
            incident_data = {
                "type": random.choice(["accident", "roadwork", "hazard", "congestion"]),
                "severity": random.choice(["low", "medium", "high", "critical"]),
                "lat": 28.6139 + random.uniform(-0.01, 0.01),
                "lng": 77.2090 + random.uniform(-0.01, 0.01),
                "description": "Simulated incident",
                "start_time": datetime.utcnow(),
                "resolved": False,
            }
            await self.incident_repo.create(incident_data)

    async def stop(self):
        self.is_running = False
        if self.sync_task:
            self.sync_task.cancel()
        logger.info("Data sync stopped")