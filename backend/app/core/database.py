from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

_db_client = None

async def connect_to_mongo():
    global _db_client

    try:
        MONGO_URI = os.getenv("MONGO_URI")

        if not MONGO_URI:
            raise Exception("MONGO_URI not set")

        _db_client = AsyncIOMotorClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=False
        )

        # Async ping
        await _db_client.admin.command("ping")

        logging.info("✅ MongoDB Connected Successfully")

    except Exception as e:
        logging.error(f"❌ MongoDB Connection Failed: {e}")


def get_db():
    return _db_client