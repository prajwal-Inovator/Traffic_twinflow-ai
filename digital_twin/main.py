# digital_twin/main.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from .twin_engine import TwinEngine
import sys
import logging

logging.basicConfig(level=logging.INFO)

async def run_twin():
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["twinflow"]
    engine = TwinEngine(db)
    await engine.initialize()
    await engine.start_updates(interval=5)
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(run_twin())