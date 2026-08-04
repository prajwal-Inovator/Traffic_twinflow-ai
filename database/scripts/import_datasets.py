#!/usr/bin/env python3
"""
Import all datasets from the datasets/ folder into MongoDB.
Run with: python database/scripts/import_datasets.py
"""
import os
import sys
import json
import csv
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from collections import defaultdict

# Add parent to path for settings
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))
from app.core.config import settings

# Map dataset number to collection name
COLLECTION_MAP = {
    '01_road_network': 'road_network',
    '02_junctions': 'junctions',
    '03_traffic_signals': 'traffic_signals',
    '04_vehicles': 'vehicles',
    '05_live_traffic': 'live_traffic',
    '06_weather': 'weather',
    '07_emergency_vehicles': 'emergency_vehicles',
    '08_hospitals': 'hospitals',
    '09_traffic_incidents': 'traffic_incidents',
    '10_traffic_cameras': 'traffic_cameras',
    '11_iot_sensors': 'iot_sensors',
    '12_public_transport': 'public_transport',
    '13_carbon_emission': 'carbon_emission',
    '14_traffic_prediction': 'traffic_prediction',
    '15_simulation': 'simulation',
    '16_driver_recommendation': 'driver_recommendation',
    '17_emergency_corridor': 'emergency_corridor',
    '18_infrastructure': 'infrastructure',
    '19_ai_decision': 'ai_decision',
    '20_feedback': 'feedback',
    '21_junction_negotiation_dataset': 'junction_negotiation',
    '22_apple_effect_dataset': 'apple_effect',
    '23_dynamic_green_wave_dataset': 'dynamic_green_wave',
    '24_signal_negotiation_log': 'signal_negotiation_log',
    '25_driver_recommendation_dataset': 'driver_recommendation_dataset',
    '26_emergency_corridor_dataset': 'emergency_corridor_dataset',
    '27_event_traffic_dataset': 'event_traffic',
    '28_weather_impact_dataset': 'weather_impact',
    '29_parking_occupancy_dataset': 'parking_occupancy',
    '30_ai_decision_history_dataset': 'ai_decision_history',
    '31_generate_winflow_datasets': 'generate_winflow_datasets',
}

async def import_csv(db, collection_name, file_path):
    """Import a CSV file into a MongoDB collection."""
    collection = db[collection_name]
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if rows:
            # Convert empty strings to None, and try to parse numbers/timestamps
            for row in rows:
                for k, v in row.items():
                    if v == '':
                        row[k] = None
                    elif v.isdigit():
                        row[k] = int(v)
                    elif v.replace('.', '', 1).isdigit():
                        row[k] = float(v)
                    # Try to parse ISO datetime
                    elif 'T' in v and (v.endswith('Z') or '+' in v):
                        try:
                            row[k] = datetime.fromisoformat(v.replace('Z', '+00:00'))
                        except:
                            pass
            # Insert all rows
            result = await collection.insert_many(rows)
            print(f"Imported {len(result.inserted_ids)} rows into {collection_name} from {file_path}")
        else:
            print(f"No data in {file_path}")

async def import_json(db, collection_name, file_path):
    """Import a JSON file into a MongoDB collection."""
    collection = db[collection_name]
    with open(file_path, 'r', encoding='utf-8') as f:
        # JSON could be an array of objects or a single object
        data = json.load(f)
        if isinstance(data, list):
            if data:
                result = await collection.insert_many(data)
                print(f"Imported {len(result.inserted_ids)} rows into {collection_name} from {file_path}")
            else:
                print(f"Empty JSON array in {file_path}")
        else:
            # Single object: insert one
            result = await collection.insert_one(data)
            print(f"Imported 1 document into {collection_name} from {file_path}")

async def import_all_datasets(datasets_dir):
    """Import all CSV/JSON files from the datasets directory."""
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    
    # Group files by base name (ignore extension)
    files = defaultdict(lambda: {'csv': None, 'json': None})
    for root, dirs, filenames in os.walk(datasets_dir):
        for filename in filenames:
            if filename.endswith('.csv') or filename.endswith('.json'):
                base = os.path.splitext(filename)[0]
                ext = os.path.splitext(filename)[1][1:]  # csv or json
                # Only process files that match our map
                if base in COLLECTION_MAP:
                    files[base][ext] = os.path.join(root, filename)
    
    for base, paths in files.items():
        collection_name = COLLECTION_MAP[base]
        # Check if collection already has data? For simplicity, we clear existing?
        # We'll not clear, just append, but we can drop if needed.
        # Let's check count and skip if data exists? We'll do a count and skip if > 0.
        count = await db[collection_name].count_documents({})
        if count > 0:
            print(f"Collection {collection_name} already has {count} documents. Skipping import to avoid duplicates.")
            continue
        
        # Import CSV if exists, else JSON
        if paths['csv']:
            await import_csv(db, collection_name, paths['csv'])
        elif paths['json']:
            await import_json(db, collection_name, paths['json'])
        else:
            print(f"No data file found for {base}")
    
    client.close()

if __name__ == "__main__":
    datasets_dir = os.path.join(os.path.dirname(__file__), '../../datasets/raw')  # adjust as needed
    if not os.path.exists(datasets_dir):
        datasets_dir = os.path.join(os.path.dirname(__file__), '../../datasets')  # fallback
    if not os.path.exists(datasets_dir):
        print(f"Datasets directory not found: {datasets_dir}")
        sys.exit(1)
    
    asyncio.run(import_all_datasets(datasets_dir))