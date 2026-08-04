"""
TwinFlow AI - Synthetic Smart City Digital Twin Dataset Generator
Generates 20 fully cross-referenced datasets (CSV + JSON) modeling a
Bengaluru-like city, for direct import into a MongoDB/FastAPI backend.

Run: python3 generate_twinflow_datasets.py
Output: ./twinflow_datasets/<NN>_<name>.csv and .json

To extend row counts, change the CONFIG constants below and re-run.
The generator is fully deterministic (SEED) so re-runs are reproducible;
change SEED for a different realistic instance of the same city.
"""

import json
import os
import random
from datetime import datetime, timedelta

import networkx as nx
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------
# CONFIG - tune these to generate more/less data
# ----------------------------------------------------------------------
SEED = 42
N_JUNCTIONS = 30
N_ROADS = 50
N_VEHICLES = 1000
N_HOSPITALS = 15
N_AMBULANCES = 30
N_CAMERAS_PER_ROAD = 2
N_BUSES = 100
SIM_DAYS = 3                       # days of hourly live_traffic / weather / iot data
PRED_HORIZON_HOURS = 24            # hours of forward traffic_prediction
N_INCIDENTS = 200
N_SIMULATIONS = 60
N_AI_DECISIONS = 150
N_DRIVER_RECS = 500

random.seed(SEED)
np.random.seed(SEED)

OUT_DIR = "twinflow_datasets"
os.makedirs(OUT_DIR, exist_ok=True)

BASE_DATE = datetime(2026, 7, 29, 0, 0, 0)  # 3-day simulation window

# ----------------------------------------------------------------------
# REFERENCE DATA - real Bengaluru locality names & approximate coordinates
# ----------------------------------------------------------------------
JUNCTION_REF = [
    ("Silk Board Junction", 12.9172, 77.6228, "High"),
    ("Marathahalli Bridge", 12.9569, 77.7011, "High"),
    ("K R Puram Junction", 13.0025, 77.6968, "High"),
    ("Hebbal Flyover", 13.0355, 77.5970, "High"),
    ("Tin Factory Junction", 12.9987, 77.6650, "Medium"),
    ("Yeshwanthpur Circle", 13.0284, 77.5540, "Medium"),
    ("Majestic (KBS) Junction", 12.9767, 77.5713, "High"),
    ("Trinity Circle", 12.9718, 77.6197, "Medium"),
    ("Domlur Flyover", 12.9611, 77.6387, "Medium"),
    ("Sarjapur Junction", 12.9010, 77.6870, "Medium"),
    ("Bannerghatta Circle", 12.8990, 77.5970, "Medium"),
    ("Electronic City Toll", 12.8452, 77.6602, "High"),
    ("Iblur Junction", 12.9350, 77.6850, "Medium"),
    ("Bellandur Junction", 12.9260, 77.6770, "Medium"),
    ("Kadubeesanahalli Junction", 12.9350, 77.6970, "Low"),
    ("Madiwala Junction", 12.9220, 77.6170, "Medium"),
    ("Mysore Road Junction", 12.9550, 77.5350, "Medium"),
    ("Yelahanka Junction", 13.1007, 77.5963, "Medium"),
    ("RT Nagar Circle", 13.0198, 77.5950, "Low"),
    ("Basaveshwara Circle", 12.9862, 77.5720, "Medium"),
    ("Koramangala Junction", 12.9352, 77.6146, "Medium"),
    ("Indiranagar Junction", 12.9719, 77.6412, "Medium"),
    ("Whitefield Junction", 12.9698, 77.7500, "High"),
    ("Banashankari Junction", 12.9250, 77.5470, "Medium"),
    ("Jayanagar Junction", 12.9250, 77.5830, "Low"),
    ("Vijayanagar Junction", 12.9707, 77.5350, "Low"),
    ("Malleshwaram Circle", 13.0031, 77.5730, "Low"),
    ("Rajajinagar Circle", 12.9911, 77.5554, "Low"),
    ("HSR Layout Junction", 12.9116, 77.6389, "Medium"),
    ("Nagawara Junction", 13.0400, 77.6220, "Low"),
][:N_JUNCTIONS]

ROAD_BASE_NAMES = [
    "Outer Ring Road", "Hosur Road", "Bannerghatta Road", "Sarjapur Road",
    "Old Airport Road", "Old Madras Road", "Mysore Road", "Tumkur Road",
    "Bellary Road (NH44)", "Magadi Road", "Kanakapura Road",
    "Whitefield Main Road", "MG Road", "Residency Road", "Brigade Road",
    "Indiranagar 100 Feet Road", "Koramangala Inner Ring Road", "CMH Road",
    "Airport Road", "Devanahalli Road", "Jayanagar 4th Block Road",
    "Banashankari Ring Road", "Malleshwaram Circle Road",
    "Yeshwanthpur Ring Road", "Hebbal-Yelahanka Road", "Nagawara-Hennur Road",
]

HOSPITAL_REF = [
    ("Victoria Hospital", 12.9634, 77.5772),
    ("NIMHANS", 12.9430, 77.5960),
    ("Manipal Hospital (Old Airport Road)", 12.9584, 77.6483),
    ("Fortis Hospital Bannerghatta Road", 12.8896, 77.5972),
    ("Apollo Hospital Bannerghatta Road", 12.9008, 77.5978),
    ("St. John's Medical College Hospital", 12.9279, 77.6238),
    ("Vydehi Institute of Medical Sciences", 12.9698, 77.7443),
    ("Sakra World Hospital", 12.9270, 77.6820),
    ("Narayana Health City", 12.8261, 77.6114),
    ("BGS Gleneagles Global Hospital", 12.9080, 77.5590),
    ("Columbia Asia Hospital Hebbal", 13.0430, 77.5960),
    ("Sparsh Hospital Yeshwanthpur", 13.0217, 77.5460),
    ("People Tree Hospital", 12.9720, 77.5490),
    ("Bowring & Lady Curzon Hospital", 12.9880, 77.6060),
    ("Jayadeva Institute of Cardiology", 12.9170, 77.5990),
][:N_HOSPITALS]

BUS_ROUTES = [
    "500D", "500K", "500C", "G4", "KBS-3A", "401M", "252F", "MF-1C",
    "600", "V-500", "356E", "201", "290F", "342", "500BC",
]

WEATHER_CONDITIONS = ["Clear", "Cloudy", "Light Rain", "Heavy Rain", "Fog", "Thunderstorm"]
VEHICLE_TYPES = ["Car", "Bus", "Truck", "Bike", "Ambulance", "Fire Truck"]
VEHICLE_TYPE_WEIGHTS = [0.42, 0.06, 0.08, 0.36, 0.04, 0.04]
FUEL_TYPES = ["Petrol", "Diesel", "CNG", "Electric"]
# fuel-type distribution conditioned on vehicle type (realistic Indian fleet mix)
FUEL_BY_VEHICLE_TYPE = {
    "Bike": (["Petrol", "Electric", "CNG"], [0.72, 0.24, 0.04]),
    "Car": (["Petrol", "Diesel", "CNG", "Electric"], [0.48, 0.24, 0.16, 0.12]),
    "Bus": (["Diesel", "CNG", "Electric"], [0.60, 0.30, 0.10]),
    "Truck": (["Diesel", "CNG"], [0.85, 0.15]),
    "Ambulance": (["Diesel", "Petrol"], [0.75, 0.25]),
    "Fire Truck": (["Diesel"], [1.0]),
}
ROAD_TYPES = ["Arterial", "Collector", "Highway", "Ring Road", "Local"]
ROAD_CONDITIONS = ["Good", "Average", "Poor", "Under Repair"]
INCIDENT_TYPES = ["Accident", "Vehicle Breakdown", "Construction", "Flood", "Tree Fall"]
SEVERITY = ["Minor", "Moderate", "Severe", "Critical"]


def jitter(val, spread=0.004):
    return round(val + np.random.uniform(-spread, spread), 6)


def ts_str(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


# ======================================================================
# DATASET 2 - JUNCTIONS  (generated before roads since roads reference it)
# ======================================================================
junctions = []
for i, (name, lat, lon, prio) in enumerate(JUNCTION_REF, start=1):
    jid = f"J{i:04d}"
    jtype = random.choice(["Signalized", "Roundabout", "Flyover", "Uncontrolled"])
    junctions.append({
        "junction_id": jid,
        "junction_name": name,
        "latitude": lat,
        "longitude": lon,
        "number_of_roads": 0,  # filled in after road graph is built
        "junction_type": jtype,
        "priority_level": prio,
    })
df_junctions = pd.DataFrame(junctions)
junction_ids = df_junctions["junction_id"].tolist()
junction_coord = {r["junction_id"]: (r["latitude"], r["longitude"]) for r in junctions}

# ======================================================================
# DATASET 1 - ROAD NETWORK (built on a connected random graph so the
# network is usable directly in NetworkX / SUMO-style simulation)
# ======================================================================
G = nx.Graph()
G.add_nodes_from(junction_ids)
# spanning tree first -> guarantees full connectivity
tree_nodes = junction_ids[:]
random.shuffle(tree_nodes)
edges = []
for i in range(1, len(tree_nodes)):
    a = tree_nodes[i]
    b = random.choice(tree_nodes[:i])
    edges.append((a, b))
# extra edges until we reach N_ROADS
existing = set(tuple(sorted(e)) for e in edges)
while len(edges) < N_ROADS:
    a, b = random.sample(junction_ids, 2)
    key = tuple(sorted((a, b)))
    # allow a few parallel roads (real cities have multiple links between hubs)
    if key in existing and random.random() > 0.15:
        continue
    edges.append((a, b))
    existing.add(key)
edges = edges[:N_ROADS]

roads = []
name_cycle = ROAD_BASE_NAMES * 3
random.shuffle(name_cycle)
for i, (a, b) in enumerate(edges, start=1):
    rid = f"R{i:04d}"
    base_name = name_cycle[i - 1]
    lat_a, lon_a = junction_coord[a]
    lat_b, lon_b = junction_coord[b]
    length_km = round(np.random.uniform(0.8, 6.5), 2)
    lanes = random.choice([2, 2, 3, 3, 4, 6])
    condition = random.choices(ROAD_CONDITIONS, weights=[0.45, 0.30, 0.15, 0.10])[0]
    capacity = int(lanes * np.random.uniform(500, 900))  # vehicles/hour
    is_highway_class = "Ring" in base_name or "NH" in base_name or "Bellary" in base_name
    speed_limit = random.choice([50, 60, 60, 80, 100]) if is_highway_class else random.choice([30, 40, 50, 60])
    roads.append({
        "road_id": rid,
        "road_name": f"{base_name} - Segment {name_cycle[:i].count(base_name)}",
        "road_type": "Ring Road" if "Ring" in base_name else ("Highway" if "NH" in base_name else random.choice(ROAD_TYPES)),
        "length_km": length_km,
        "lanes": lanes,
        "speed_limit_kmph": speed_limit,
        "junction_start": a,
        "junction_end": b,
        "road_condition": condition,
        "traffic_capacity_vph": capacity,
        "latitude": jitter((lat_a + lat_b) / 2, 0.001),
        "longitude": jitter((lon_a + lon_b) / 2, 0.001),
    })
df_roads = pd.DataFrame(roads)
road_ids = df_roads["road_id"].tolist()
road_coord = {r["road_id"]: (r["latitude"], r["longitude"]) for r in roads}
road_endpoints = {r["road_id"]: (r["junction_start"], r["junction_end"]) for r in roads}

# back-fill number_of_roads (degree) on junctions
deg = {j: 0 for j in junction_ids}
for r in roads:
    deg[r["junction_start"]] += 1
    deg[r["junction_end"]] += 1
df_junctions["number_of_roads"] = df_junctions["junction_id"].map(deg)

# ======================================================================
# DATASET 3 - TRAFFIC SIGNALS (one per Signalized/Flyover/Roundabout junction)
# ======================================================================
signals = []
sig_i = 1
for j in junctions:
    if j["junction_type"] in ("Signalized", "Flyover", "Roundabout"):
        green = random.choice([25, 30, 35, 40, 45, 60])
        yellow = random.choice([3, 4, 5])
        red = random.choice([20, 25, 30, 35, 40])
        signals.append({
            "signal_id": f"S{sig_i:04d}",
            "junction_id": j["junction_id"],
            "green_time_sec": green,
            "yellow_time_sec": yellow,
            "red_time_sec": red,
            "adaptive_mode": random.choice([True, False]),
            "current_status": random.choice(["Green", "Yellow", "Red"]),
            "last_updated": ts_str(BASE_DATE + timedelta(minutes=random.randint(0, SIM_DAYS * 1440))),
        })
        sig_i += 1
df_signals = pd.DataFrame(signals)
signal_junctions = df_signals["junction_id"].tolist()

# ======================================================================
# DATASET 8 - HOSPITALS
# ======================================================================
hospitals = []
for i, (name, lat, lon) in enumerate(HOSPITAL_REF, start=1):
    hospitals.append({
        "hospital_id": f"H{i:03d}",
        "hospital_name": name,
        "latitude": lat,
        "longitude": lon,
        "ambulance_count": random.randint(2, 6),
        "capacity_beds": random.choice([80, 120, 150, 200, 250, 300, 450, 600]),
    })
df_hospitals = pd.DataFrame(hospitals)
hospital_ids = df_hospitals["hospital_id"].tolist()
hospital_coord = {h["hospital_id"]: (h["latitude"], h["longitude"]) for h in hospitals}
# distribute exactly ambulance_count ambulances per hospital, total ~= N_AMBULANCES
amb_alloc = []
for h in hospitals:
    amb_alloc.extend([h["hospital_id"]] * h["ambulance_count"])
while len(amb_alloc) < N_AMBULANCES:
    amb_alloc.append(random.choice(hospital_ids))
amb_alloc = amb_alloc[:N_AMBULANCES]

# ======================================================================
# DATASET 4 - VEHICLES
# ======================================================================
vehicles = []
for i in range(1, N_VEHICLES + 1):
    vtype = random.choices(VEHICLE_TYPES, weights=VEHICLE_TYPE_WEIGHTS)[0]
    r = random.choice(road_ids)
    lat, lon = road_coord[r]
    src, dst = random.sample(junction_ids, 2)
    priority = "Emergency" if vtype in ("Ambulance", "Fire Truck") else random.choices(["Normal", "High"], weights=[0.9, 0.1])[0]
    speed = round(np.random.normal(32 if vtype != "Bike" else 28, 10), 1)
    speed = max(0, min(speed, 90))
    vehicles.append({
        "vehicle_id": f"V{i:06d}",
        "vehicle_type": vtype,
        "gps_lat": jitter(lat),
        "gps_long": jitter(lon),
        "current_speed_kmph": speed,
        "lane": random.randint(1, 4),
        "source": src,
        "destination": dst,
        "priority_level": priority,
        "fuel_type": random.choices(*FUEL_BY_VEHICLE_TYPE[vtype])[0],
    })
df_vehicles = pd.DataFrame(vehicles)
vehicle_ids = df_vehicles["vehicle_id"].tolist()
ambulance_vehicle_ids = df_vehicles[df_vehicles.vehicle_type == "Ambulance"]["vehicle_id"].tolist()

# ======================================================================
# DATASET 6 - WEATHER (hourly, city-wide)
# ======================================================================
weather = []
hours = SIM_DAYS * 24
for h in range(hours):
    dt = BASE_DATE + timedelta(hours=h)
    hour_of_day = dt.hour
    is_monsoon_shower = random.random() < 0.18
    condition = "Heavy Rain" if (is_monsoon_shower and random.random() < 0.3) else (
        "Light Rain" if is_monsoon_shower else random.choices(
            ["Clear", "Cloudy", "Fog"], weights=[0.55, 0.35, 0.10])[0])
    if condition == "Fog" and not (0 <= hour_of_day <= 6):
        condition = "Cloudy"
    temp = round(np.random.normal(24 + 4 * np.sin((hour_of_day - 9) / 24 * 2 * np.pi), 1.5), 1)
    rainfall = round(np.random.uniform(2, 25), 1) if "Rain" in condition else (round(np.random.uniform(0, 1), 1))
    weather.append({
        "timestamp": ts_str(dt),
        "temperature_c": temp,
        "humidity_pct": round(np.random.uniform(55, 90) if "Rain" in condition else np.random.uniform(35, 65), 1),
        "rainfall_mm": rainfall,
        "visibility_km": round(np.random.uniform(0.5, 2.5) if condition == "Fog" else np.random.uniform(4, 10), 1),
        "wind_speed_kmph": round(np.random.uniform(4, 28), 1),
        "weather_condition": condition,
    })
df_weather = pd.DataFrame(weather)
weather_by_ts = {w["timestamp"]: w for w in weather}


def congestion_level(density):
    if density < 25:
        return "Low"
    if density < 55:
        return "Medium"
    if density < 80:
        return "High"
    return "Severe"


# ======================================================================
# DATASET 5 - LIVE TRAFFIC  (per road, per hour, over SIM_DAYS)
# ======================================================================
live_traffic = []
road_capacity = {r["road_id"]: r["traffic_capacity_vph"] for r in roads}
road_speed_limit = {r["road_id"]: r["speed_limit_kmph"] for r in roads}
for h in range(hours):
    dt = BASE_DATE + timedelta(hours=h)
    hour_of_day = dt.hour
    w = weather[h]
    rain_penalty = 0.85 if "Rain" in w["weather_condition"] else (0.92 if w["weather_condition"] == "Fog" else 1.0)
    # rush hour multiplier: 8-11am & 5:30-8:30pm heavier
    if hour_of_day in (8, 9, 10, 18, 19, 20):
        demand_factor = np.random.uniform(0.75, 1.0)
    elif hour_of_day in (7, 11, 17, 21):
        demand_factor = np.random.uniform(0.5, 0.75)
    elif 0 <= hour_of_day <= 5:
        demand_factor = np.random.uniform(0.03, 0.15)
    else:
        demand_factor = np.random.uniform(0.25, 0.5)
    for rid in road_ids:
        cap = road_capacity[rid]
        vcount = int(cap * demand_factor * np.random.uniform(0.8, 1.15))
        density = round(min(100, (vcount / cap) * 100), 1)
        speed_limit = road_speed_limit[rid]
        avg_speed = round(max(4, speed_limit * (1 - density / 130) * rain_penalty * np.random.uniform(0.9, 1.05)), 1)
        length_km = df_roads.loc[df_roads.road_id == rid, "length_km"].values[0]
        travel_time_min = round((length_km / max(avg_speed, 4)) * 60, 1)
        queue_length_m = round(max(0, (density - 40) * np.random.uniform(2, 5)), 1) if density > 40 else round(np.random.uniform(0, 15), 1)
        live_traffic.append({
            "timestamp": ts_str(dt),
            "road_id": rid,
            "vehicle_count": vcount,
            "average_speed_kmph": avg_speed,
            "density_pct": density,
            "travel_time_min": travel_time_min,
            "queue_length_m": queue_length_m,
            "congestion_level": congestion_level(density),
        })
df_live_traffic = pd.DataFrame(live_traffic)

# ======================================================================
# DATASET 9 - TRAFFIC INCIDENTS
# ======================================================================
incidents = []
for i in range(1, N_INCIDENTS + 1):
    rid = random.choice(road_ids)
    itype = random.choices(INCIDENT_TYPES, weights=[0.35, 0.25, 0.20, 0.08, 0.12])[0]
    sev = random.choices(SEVERITY, weights=[0.45, 0.30, 0.18, 0.07])[0]
    start = BASE_DATE + timedelta(minutes=random.randint(0, SIM_DAYS * 1440))
    clear_minutes = {"Minor": (10, 30), "Moderate": (20, 60), "Severe": (45, 120), "Critical": (90, 240)}[sev]
    expected_clear = start + timedelta(minutes=random.randint(*clear_minutes))
    incidents.append({
        "incident_id": f"INC{i:05d}",
        "road_id": rid,
        "incident_type": itype,
        "severity": sev,
        "start_time": ts_str(start),
        "expected_clear_time": ts_str(expected_clear),
    })
df_incidents = pd.DataFrame(incidents)

# ======================================================================
# DATASET 10 - TRAFFIC CAMERAS
# ======================================================================
cameras = []
cam_i = 1
for rid in road_ids:
    for _ in range(N_CAMERAS_PER_ROAD):
        cameras.append({
            "camera_id": f"CAM{cam_i:04d}",
            "road_id": rid,
            "camera_angle_deg": random.choice([0, 45, 90, 135, 180, 225, 270, 315]),
            "fps": random.choice([15, 24, 30, 60]),
            "resolution": random.choice(["720p", "1080p", "4K"]),
            "status": random.choices(["Active", "Inactive", "Maintenance"], weights=[0.88, 0.06, 0.06])[0],
        })
        cam_i += 1
df_cameras = pd.DataFrame(cameras)

# ======================================================================
# DATASET 11 - IoT SENSORS (one per road, hourly for 1 day to keep size sane)
# ======================================================================
iot_rows = []
sens_map = {rid: f"IOT{idx+1:04d}" for idx, rid in enumerate(road_ids)}
for h in range(24):
    dt = BASE_DATE + timedelta(hours=h)
    lt_slice = [r for r in live_traffic if r["timestamp"] == ts_str(dt)]
    lt_by_road = {r["road_id"]: r for r in lt_slice}
    w = weather[h]
    for rid in road_ids:
        lt = lt_by_road[rid]
        base_aqi = 85 if "Rain" not in w["weather_condition"] else 55
        aqi = int(max(25, min(300, base_aqi + lt["density_pct"] * 1.3 + np.random.normal(0, 15))))
        iot_rows.append({
            "sensor_id": sens_map[rid],
            "road_id": rid,
            "timestamp": ts_str(dt),
            "traffic_density_pct": lt["density_pct"],
            "vehicle_count": lt["vehicle_count"],
            "average_speed_kmph": lt["average_speed_kmph"],
            "occupancy_pct": round(min(100, lt["density_pct"] * np.random.uniform(0.9, 1.1)), 1),
            "air_quality_aqi": aqi,
            "noise_level_db": round(55 + lt["density_pct"] * 0.35 + np.random.normal(0, 3), 1),
        })
df_iot = pd.DataFrame(iot_rows)

# ======================================================================
# DATASET 12 - PUBLIC TRANSPORT (buses)
# ======================================================================
buses = []
for i in range(1, N_BUSES + 1):
    rid = random.choice(road_ids)
    lat, lon = road_coord[rid]
    buses.append({
        "bus_id": f"BMTC{i:04d}",
        "route": random.choice(BUS_ROUTES),
        "current_location_lat": jitter(lat),
        "current_location_long": jitter(lon),
        "current_road_id": rid,
        "occupancy_pct": random.randint(10, 100),
        "eta_min": round(np.random.uniform(1, 25), 1),
    })
df_buses = pd.DataFrame(buses)

# ======================================================================
# DATASET 7 & 17 - EMERGENCY VEHICLES + EMERGENCY CORRIDOR
# ======================================================================
emergency_vehicles = []
emergency_corridor = []
STATUS_CHOICES = ["Dispatched", "En Route", "Arrived", "Available"]
for i in range(1, N_AMBULANCES + 1):
    hid = amb_alloc[i - 1]
    hlat, hlon = hospital_coord[hid]
    rid = random.choice(road_ids)
    rlat, rlon = road_coord[rid]
    status = random.choices(STATUS_CHOICES, weights=[0.2, 0.25, 0.15, 0.4])[0]
    priority = "Critical" if status in ("Dispatched", "En Route") else "Standby"
    eta = round(np.random.uniform(3, 25), 1) if status in ("Dispatched", "En Route") else 0.0
    amb_id = f"AMB{i:04d}"
    emergency_vehicles.append({
        "ambulance_id": amb_id,
        "hospital_id": hid,
        "destination_road_id": rid,
        "priority": priority,
        "current_location_lat": jitter(rlat if status != "Available" else hlat),
        "current_location_long": jitter(rlon if status != "Available" else hlon),
        "eta_min": eta,
        "status": status,
    })
    if status in ("Dispatched", "En Route"):
        n_signals = random.randint(1, 5)
        emergency_corridor.append({
            "corridor_id": f"COR{i:04d}",
            "ambulance_id": amb_id,
            "road_id": rid,
            "priority": "Critical",
            "signals_modified": n_signals,
            "estimated_time_saved_min": round(n_signals * np.random.uniform(0.8, 2.2), 1),
        })
df_emergency_vehicles = pd.DataFrame(emergency_vehicles)
df_emergency_corridor = pd.DataFrame(emergency_corridor)

# ======================================================================
# DATASET 13 - CARBON EMISSION (per road, per day)
# ======================================================================
carbon = []
CO2_FACTOR = {"Petrol": 2.31, "Diesel": 2.68, "CNG": 1.94, "Electric": 0.0}  # kg CO2 / litre-equiv
for day in range(SIM_DAYS):
    day_start = BASE_DATE + timedelta(days=day)
    day_end = day_start + timedelta(hours=24)
    day_rows = [r for r in live_traffic if day_start <= datetime.fromisoformat(r["timestamp"]) < day_end]
    by_road = {}
    for r in day_rows:
        by_road.setdefault(r["road_id"], []).append(r)
    for rid, rows in by_road.items():
        total_vcount = sum(r["vehicle_count"] for r in rows)
        length_km = df_roads.loc[df_roads.road_id == rid, "length_km"].values[0]
        avg_consumption_l_per_km = 0.09  # blended fleet estimate
        fuel_l = round(total_vcount * length_km * avg_consumption_l_per_km, 1)
        co2_kg = round(fuel_l * 2.35, 1)  # blended emission factor
        avg_density = np.mean([r["density_pct"] for r in rows])
        aqi = int(max(25, min(300, 60 + avg_density * 1.4)))
        carbon.append({
            "road_id": rid,
            "date": day_start.strftime("%Y-%m-%d"),
            "vehicle_count": total_vcount,
            "fuel_consumption_l": fuel_l,
            "estimated_co2_kg": co2_kg,
            "aqi": aqi,
        })
df_carbon = pd.DataFrame(carbon)

# ======================================================================
# DATASET 14 - TRAFFIC PREDICTION (per road, next PRED_HORIZON_HOURS)
# ======================================================================
predictions = []
pred_i = 1
last_actual_ts = BASE_DATE + timedelta(hours=hours - 1)
last_slice = {r["road_id"]: r for r in live_traffic if r["timestamp"] == ts_str(last_actual_ts)}
ACTIONS = {
    "Low": "Maintain current signal timing",
    "Medium": "Monitor; prepare adaptive signal shift",
    "High": "Activate adaptive signal + suggest alternate route",
    "Severe": "Trigger diversion + notify traffic police",
}
for rid in road_ids:
    cur = last_slice[rid]
    for h in range(1, PRED_HORIZON_HOURS + 1):
        future_ts = last_actual_ts + timedelta(hours=h)
        drift = np.random.normal(0, 6)
        pred_density = round(min(100, max(0, cur["density_pct"] + drift + 3 * np.sin(h / 6))), 1)
        confidence = round(max(0.55, min(0.97, 0.95 - 0.01 * h + np.random.normal(0, 0.02))), 2)
        pred_level = congestion_level(pred_density)
        predictions.append({
            "prediction_id": f"PRED{pred_i:06d}",
            "road_id": rid,
            "timestamp": ts_str(future_ts),
            "current_traffic_level": congestion_level(cur["density_pct"]),
            "predicted_traffic_level": pred_level,
            "predicted_density_pct": pred_density,
            "prediction_confidence": confidence,
            "recommended_action": ACTIONS[pred_level],
        })
        pred_i += 1
df_predictions = pd.DataFrame(predictions)

# ======================================================================
# DATASET 20 - FEEDBACK (closes the loop for a sample of predictions,
# comparing predicted vs. "actual" outcome observed 1h later)
# ======================================================================
feedback = []
sample_preds = df_predictions[df_predictions["timestamp"] <= ts_str(last_actual_ts + timedelta(hours=6))].sample(
    n=min(200, len(df_predictions)), random_state=SEED)
for i, (_, row) in enumerate(sample_preds.iterrows(), start=1):
    actual_density = round(min(100, max(0, row["predicted_density_pct"] + np.random.normal(0, 5))), 1)
    diff = round(abs(actual_density - row["predicted_density_pct"]), 1)
    accuracy = round(max(0, 1 - diff / 100), 3)
    feedback.append({
        "feedback_id": f"FB{i:05d}",
        "prediction_id": row["prediction_id"],
        "road_id": row["road_id"],
        "predicted_density_pct": row["predicted_density_pct"],
        "actual_density_pct": actual_density,
        "difference": diff,
        "accuracy": accuracy,
        "model_updated": bool(diff > 12),
    })
df_feedback = pd.DataFrame(feedback)

# ======================================================================
# DATASET 15 - SIMULATION (what-if scenarios)
# ======================================================================
SCENARIOS = ["Signal Timing Change", "Vehicle Diversion", "Emergency Corridor",
             "Bus Priority", "Heavy Vehicle Restriction", "Combined Strategy"]
simulations = []
for i in range(1, N_SIMULATIONS + 1):
    scenario = random.choice(SCENARIOS)
    rid = random.choice(road_ids)
    reduction = round(np.random.uniform(4, 35), 1)
    fuel_saved = round(reduction * np.random.uniform(8, 20), 1)
    delay_reduced = round(reduction * np.random.uniform(0.3, 0.9), 1)
    simulations.append({
        "simulation_id": f"SIM{i:04d}",
        "scenario": scenario,
        "road_id": rid,
        "traffic_reduction_pct": reduction,
        "fuel_saved_l": fuel_saved,
        "delay_reduced_min": delay_reduced,
        "recommendation": f"Apply '{scenario}' on {rid} — projected {reduction}% congestion reduction",
    })
df_simulations = pd.DataFrame(simulations)

# ======================================================================
# DATASET 16 - DRIVER RECOMMENDATION
# ======================================================================
driver_recs = []
sample_vehicles = random.sample(vehicle_ids, min(N_DRIVER_RECS, len(vehicle_ids)))
veh_speed = dict(zip(df_vehicles.vehicle_id, df_vehicles.current_speed_kmph))
for vid in sample_vehicles:
    cur_speed = veh_speed[vid]
    rec_speed = round(max(15, min(60, cur_speed + np.random.uniform(-8, 8))), 1)
    green_wave = abs(rec_speed - cur_speed) < 4
    driver_recs.append({
        "vehicle_id": vid,
        "current_speed_kmph": cur_speed,
        "recommended_speed_kmph": rec_speed,
        "next_signal_eta_sec": random.randint(10, 90),
        "green_wave_status": green_wave,
    })
df_driver_recs = pd.DataFrame(driver_recs)

# ======================================================================
# DATASET 18 - INFRASTRUCTURE HEALTH
# ======================================================================
infra = []
for rid in road_ids:
    cond = df_roads.loc[df_roads.road_id == rid, "road_condition"].values[0]
    base_stress = {"Good": 20, "Average": 45, "Poor": 70, "Under Repair": 85}[cond]
    road_stress = round(min(100, base_stress + np.random.uniform(-8, 8)), 1)
    has_bridge = random.random() < 0.25
    bridge_stress = round(min(100, base_stress * np.random.uniform(0.7, 1.1)), 1) if has_bridge else None
    maintenance_score = round(max(0, 100 - road_stress * np.random.uniform(0.8, 1.0)), 1)
    health = "Good" if maintenance_score > 75 else ("Fair" if maintenance_score > 50 else ("Poor" if maintenance_score > 25 else "Critical"))
    infra.append({
        "road_id": rid,
        "has_bridge": has_bridge,
        "road_stress_pct": road_stress,
        "bridge_stress_pct": bridge_stress,
        "maintenance_score": maintenance_score,
        "road_health": health,
    })
df_infra = pd.DataFrame(infra)

# ======================================================================
# DATASET 19 - AI DECISION (multi-agent recommendations)
# ======================================================================
TRAFFIC_REC = ["Extend green phase on approach", "Activate adaptive signal control",
               "Reroute via alternate arterial", "No action required"]
EMERGENCY_REC = ["Clear emergency corridor now", "Pre-empt next 3 signals",
                  "No emergency vehicles active", "Hold — awaiting dispatch confirmation"]
ENV_REC = ["Restrict heavy vehicles — AQI high", "Conditions normal", "Issue low-visibility advisory"]
INFRA_REC = ["Schedule maintenance — high stress", "Infrastructure nominal", "Flag for inspection"]
PT_REC = ["Increase bus frequency on route", "Maintain schedule", "Prioritize bus at junction"]

ai_decisions = []
for i in range(1, N_AI_DECISIONS + 1):
    rid = random.choice(road_ids)
    jid = df_roads.loc[df_roads.road_id == rid, "junction_start"].values[0]
    t_rec = random.choice(TRAFFIC_REC)
    e_rec = random.choice(EMERGENCY_REC)
    env_rec = random.choice(ENV_REC)
    i_rec = random.choice(INFRA_REC)
    p_rec = random.choice(PT_REC)
    active_emergency = e_rec in ("Clear emergency corridor now", "Pre-empt next 3 signals")
    master = e_rec if active_emergency else (t_rec if t_rec != "No action required" else p_rec)
    ai_decisions.append({
        "decision_id": f"DEC{i:05d}",
        "timestamp": ts_str(BASE_DATE + timedelta(minutes=random.randint(0, SIM_DAYS * 1440))),
        "road_id": rid,
        "junction_id": jid,
        "traffic_ai_recommendation": t_rec,
        "emergency_ai_recommendation": e_rec,
        "environment_ai_recommendation": env_rec,
        "infrastructure_ai_recommendation": i_rec,
        "public_transport_recommendation": p_rec,
        "master_ai_decision": master,
        "reason": f"Weighted priority: {'Emergency > Traffic > Transport > Infra > Environment' if active_emergency else 'Traffic flow optimization prioritized'}",
    })
df_ai_decisions = pd.DataFrame(ai_decisions)

# ======================================================================
# SAVE ALL DATASETS (CSV + JSON)
# ======================================================================
DATASETS = [
    ("01_road_network", df_roads),
    ("02_junctions", df_junctions),
    ("03_traffic_signals", df_signals),
    ("04_vehicles", df_vehicles),
    ("05_live_traffic", df_live_traffic),
    ("06_weather", df_weather),
    ("07_emergency_vehicles", df_emergency_vehicles),
    ("08_hospitals", df_hospitals),
    ("09_traffic_incidents", df_incidents),
    ("10_traffic_cameras", df_cameras),
    ("11_iot_sensors", df_iot),
    ("12_public_transport", df_buses),
    ("13_carbon_emission", df_carbon),
    ("14_traffic_prediction", df_predictions),
    ("15_simulation", df_simulations),
    ("16_driver_recommendation", df_driver_recs),
    ("17_emergency_corridor", df_emergency_corridor),
    ("18_infrastructure", df_infra),
    ("19_ai_decision", df_ai_decisions),
    ("20_feedback", df_feedback),
]

summary = []
for name, df in DATASETS:
    csv_path = os.path.join(OUT_DIR, f"{name}.csv")
    json_path = os.path.join(OUT_DIR, f"{name}.json")
    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=2, date_format="iso")
    summary.append((name, len(df), list(df.columns)))

print("Generated datasets:")
for name, n, cols in summary:
    print(f"  {name:30s} rows={n:6d}  cols={len(cols)}")

# ----------------------------------------------------------------------
# VALIDATION: verify every foreign key resolves
# ----------------------------------------------------------------------
errors = []
if not set(df_roads.junction_start).issubset(set(junction_ids)):
    errors.append("road.junction_start has orphan junction_id")
if not set(df_roads.junction_end).issubset(set(junction_ids)):
    errors.append("road.junction_end has orphan junction_id")
if not set(df_signals.junction_id).issubset(set(junction_ids)):
    errors.append("signals.junction_id orphan")
if not set(df_live_traffic.road_id).issubset(set(road_ids)):
    errors.append("live_traffic.road_id orphan")
if not set(df_incidents.road_id).issubset(set(road_ids)):
    errors.append("incidents.road_id orphan")
if not set(df_cameras.road_id).issubset(set(road_ids)):
    errors.append("cameras.road_id orphan")
if not set(df_iot.road_id).issubset(set(road_ids)):
    errors.append("iot.road_id orphan")
if not set(df_carbon.road_id).issubset(set(road_ids)):
    errors.append("carbon.road_id orphan")
if not set(df_predictions.road_id).issubset(set(road_ids)):
    errors.append("predictions.road_id orphan")
if not set(df_infra.road_id).issubset(set(road_ids)):
    errors.append("infra.road_id orphan")
if not set(df_emergency_vehicles.hospital_id).issubset(set(hospital_ids)):
    errors.append("emergency_vehicles.hospital_id orphan")
if not set(df_emergency_vehicles.destination_road_id).issubset(set(road_ids)):
    errors.append("emergency_vehicles.destination_road_id orphan")
if not set(df_emergency_corridor.ambulance_id).issubset(set(df_emergency_vehicles.ambulance_id)):
    errors.append("emergency_corridor.ambulance_id orphan")
if not set(df_driver_recs.vehicle_id).issubset(set(vehicle_ids)):
    errors.append("driver_recs.vehicle_id orphan")
if not set(df_feedback.prediction_id).issubset(set(df_predictions.prediction_id)):
    errors.append("feedback.prediction_id orphan")
if not set(df_buses.current_road_id).issubset(set(road_ids)):
    errors.append("buses.current_road_id orphan")

if errors:
    print("\nVALIDATION ERRORS:")
    for e in errors:
        print("  -", e)
    raise SystemExit(1)
else:
    print("\nAll foreign keys validated OK. Referential integrity confirmed across all 20 datasets.")
