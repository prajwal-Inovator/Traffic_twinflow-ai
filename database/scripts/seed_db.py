#!/usr/bin/env python3
"""
Database seeding script for TwinFlow AI.
Run with: python database/scripts/seed_db.py
"""
import asyncio
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import sys

# Add parent directory to path to import settings
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_users(db):
    """Seed default users."""
    users_collection = db["users"]
    
    # Check if users already exist
    count = await users_collection.count_documents({})
    if count > 0:
        print("Users already exist, skipping seed.")
        return
    
    # Load users from JSON file (or define inline)
    seed_path = os.path.join(os.path.dirname(__file__), '../seeds/default_users.json')
    if os.path.exists(seed_path):
        with open(seed_path, 'r') as f:
            users_data = json.load(f)
    else:
        # Fallback: define default users
        users_data = [
            {
                "email": "admin@twinflow.ai",
                "full_name": "System Admin",
                "role": "admin",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            {
                "email": "authority@city.gov",
                "full_name": "City Authority",
                "role": "authority",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            {
                "email": "driver1@example.com",
                "full_name": "Driver One",
                "role": "driver",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            {
                "email": "emergency@fire.gov",
                "full_name": "Emergency Services",
                "role": "emergency",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        ]
    
    # Hash passwords (default password: "password123")
    default_password = "password123"
    for user in users_data:
        user["hashed_password"] = pwd_context.hash(default_password)
        if "created_at" in user and isinstance(user["created_at"], str):
            # Handle JSON date if loaded from file
            pass
        # Convert to proper datetime if needed
        if "created_at" in user and isinstance(user["created_at"], dict):
            # Handle $date format from JSON
            if "$date" in user["created_at"]:
                user["created_at"] = datetime.fromisoformat(user["created_at"]["$date"].replace('Z', '+00:00'))
        if "updated_at" in user and isinstance(user["updated_at"], dict):
            if "$date" in user["updated_at"]:
                user["updated_at"] = datetime.fromisoformat(user["updated_at"]["$date"].replace('Z', '+00:00'))
    
    # Insert users
    result = await users_collection.insert_many(users_data)
    print(f"Inserted {len(result.inserted_ids)} users.")

async def seed_junctions(db):
    """Seed default junctions."""
    junctions_collection = db["junctions"]  # We'll store junction state in this collection
    
    # Check if junctions already exist
    count = await junctions_collection.count_documents({})
    if count > 0:
        print("Junctions already exist, skipping seed.")
        return
    
    seed_path = os.path.join(os.path.dirname(__file__), '../seeds/default_junctions.json')
    if os.path.exists(seed_path):
        with open(seed_path, 'r') as f:
            junctions_data = json.load(f)
    else:
        junctions_data = [
            {
                "id": "J001",
                "name": "Connaught Place",
                "lat": 28.6304,
                "lng": 77.2177,
                "vehicle_count": 0,
                "queue_length": 0,
                "signal_phase": "green",
                "green_time": 60,
                "red_time": 30,
                "emergency_status": False,
                "bus_priority": False,
                "pollution": 85,
                "weather": "clear",
                "current_delay": 0,
                "predicted_vehicles": 0,
                "created_at": datetime.utcnow(),
            },
            {
                "id": "J002",
                "name": "India Gate",
                "lat": 28.6129,
                "lng": 77.2295,
                "vehicle_count": 0,
                "queue_length": 0,
                "signal_phase": "red",
                "green_time": 45,
                "red_time": 45,
                "emergency_status": False,
                "bus_priority": False,
                "pollution": 78,
                "weather": "clear",
                "current_delay": 0,
                "predicted_vehicles": 0,
                "created_at": datetime.utcnow(),
            }
        ]
    
    # Insert junctions
    result = await junctions_collection.insert_many(junctions_data)
    print(f"Inserted {len(result.inserted_ids)} junctions.")

async def main():
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    
    print("Seeding database...")
    await seed_users(db)
    await seed_junctions(db)
    print("Seeding complete.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())