# backend/app/core/indexes.py
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from .database import get_db

logger = logging.getLogger(__name__)

async def ensure_indexes():
    """Create all required indexes if they don't exist."""
    db = get_db()
    
    # Users
    await db.users.create_index("email", unique=True)
    await db.users.create_index("role")
    
    # Vehicles
    await db.vehicles.create_index([("timestamp", -1)])
    await db.vehicles.create_index("junction_id")
    await db.vehicles.create_index("type")
    
    # Signals
    await db.signals.create_index("junction_id", unique=True)
    
    # Roads
    await db.roads.create_index([("start_junction_id", 1), ("end_junction_id", 1)])
    
    # Predictions
    await db.predictions.create_index([("junction_id", 1), ("timestamp", -1)])
    await db.predictions.create_index("horizon_minutes")
    
    # Negotiation messages
    await db.negotiation_messages.create_index([("junction_id", 1), ("timestamp", -1)])
    
    # Recommendations (Master)
    await db.recommendations.create_index([("junction_id", 1), ("timestamp", -1)])
    
    # Incidents
    await db.incidents.create_index("resolved")
    await db.incidents.create_index("severity")
    await db.incidents.create_index([("start_time", -1)])
    
    # Simulation results
    await db.simulation_results.create_index([("junction_id", 1), ("time_horizon", 1)])
    await db.simulation_results.create_index("simulation_id")
    
    # Carbon reports
    await db.carbon_reports.create_index([("junction_id", 1), ("date", -1)])
    
    logger.info("All MongoDB indexes ensured.")