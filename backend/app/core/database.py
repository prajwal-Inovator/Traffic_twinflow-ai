# backend/app/core/database.py
import motor.motor_asyncio
from typing import Optional
from ..core.config import settings

_db_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
_db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None

async def connect_to_mongo():
    global _db_client, _db
    _db_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
    _db = _db_client[settings.MONGO_DB_NAME]
    # Test connection
    await _db_client.admin.command("ping")

async def close_mongo_connection():
    global _db_client
    if _db_client:
        _db_client.close()
        _db_client = None

def get_db() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not connected")
    return _db