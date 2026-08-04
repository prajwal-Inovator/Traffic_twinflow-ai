# TwinFlow AI — Synthetic Smart City Dataset Pack
### Bengaluru Digital Twin — 20 cross-referenced datasets, ready for backend import

Generated deterministically (seed=42) by `generate_twinflow_datasets.py`. Every foreign key in
this pack has been programmatically validated — there are no orphan IDs. Re-run the script any
time to regenerate a fresh, equally-consistent instance, or edit the `CONFIG` block at the top
to scale row counts up (e.g. more days of live_traffic, more vehicles, more junctions).

City reference frame: real Bengaluru locality names and coordinates (Silk Board, Marathahalli,
Hebbal, Whitefield, Electronic City, etc.), a 30-node/50-edge connected road graph (built with
NetworkX so it drops straight into `nx.Graph()` or SUMO's `netconvert`), and a 3-day simulation
window starting **2026-07-29T00:00:00**.

Every file is provided as both **`.csv`** and **`.json`** (`records` orient, ready for
`db.collection.insertMany()`).

---

## Entity-Relationship Overview

```
                         ┌────────────┐
                         │ junctions  │  PK: junction_id
                         └─────┬──────┘
                    ┌──────────┼───────────────┐
                    │          │               │
             junction_start  junction_id   source/destination
                    │          │               │
             ┌──────▼──────┐  ┌▼───────────┐  ┌▼──────────┐
             │    roads     │  │  signals   │  │  vehicles │
             │ PK: road_id  │  └────────────┘  │PK:vehicle_│
             └──────┬───────┘                  │    id     │
     ┌───────┬──────┼──────┬────────┬──────────┴─┬─────────┐
     │       │      │      │        │            │         │
┌────▼───┐ ┌─▼────┐┌▼─────┐┌▼──────┐┌▼─────────┐ ┌▼────────┐
│live_    │ │incid-││camer-││iot_   ││carbon_    │ │driver_  │
│traffic  │ │ents  ││as    ││sensors││emission   │ │recs     │
└─────────┘ └──────┘└──────┘└───────┘└───────────┘ └─────────┘
     │
┌────▼─────────┐        ┌────────────┐       ┌───────────────┐
│traffic_       │──PK──▶│  feedback  │       │ infrastructure │ (1:1 with road_id)
│prediction     │       └────────────┘       └────────────────┘

┌────────────┐      ┌──────────────┐      ┌────────────────────┐
│ hospitals  │─────▶│  emergency_  │─────▶│ emergency_corridor  │
│PK:hospital_│ (FK  │  vehicles    │ (FK   └────────────────────┘
│    id      │ hosp.│PK:ambulance_ │ ambul.
└────────────┘ id)  │    id        │ id)
                     └──────────────┘

┌────────────┐               ┌────────────────┐
│ simulation │ (references   │  ai_decision    │ (references
│  (road_id) │  road_id)     │ (road_id +      │  road_id + junction_id,
└────────────┘               │  junction_id)   │  synthesizes all agent outputs)
                              └─────────────────┘

┌───────────────┐
│public_transport│ (references road_id via current_road_id)
└───────────────┘

┌──────────┐
│ weather  │ (city-wide, joined to any table by nearest timestamp — no FK)
└──────────┘
```

---

## Dataset 1 — `01_road_network` (50 rows)

| Column | Type | Description |
|---|---|---|
| `road_id` **PK** | string | `R0001`–`R0050` |
| `road_name` | string | Real Bengaluru arterial/ring-road name + segment number |
| `road_type` | enum | Arterial / Collector / Highway / Ring Road / Local |
| `length_km` | float | 0.8–6.5 km |
| `lanes` | int | 2–6 |
| `speed_limit_kmph` | int | 30–60 (surface roads), 50–100 (highway/ring-road class) |
| `junction_start` **FK→junctions.junction_id** | string | |
| `junction_end` **FK→junctions.junction_id** | string | |
| `road_condition` | enum | Good / Average / Poor / Under Repair |
| `traffic_capacity_vph` | int | Vehicles/hour theoretical capacity |
| `latitude`, `longitude` | float | Midpoint of the road segment |

**Sample:**
```json
{
  "road_id": "R0001",
  "road_name": "Bellary Road (NH44) - Segment 1",
  "road_type": "Highway",
  "length_km": 2.93,
  "lanes": 2,
  "speed_limit_kmph": 50,
  "junction_start": "J0019",
  "junction_end": "J0025",
  "road_condition": "Good",
  "traffic_capacity_vph": 1760,
  "latitude": 12.972864,
  "longitude": 77.589197
}
```
**MongoDB collection:** `roads`
**Validation rules:** `road_id` unique; `junction_start != junction_end`; `lanes ≥ 1`; `speed_limit_kmph ≤ 100`.

---

## Dataset 2 — `02_junctions` (30 rows)

| Column | Type | Description |
|---|---|---|
| `junction_id` **PK** | string | `J0001`–`J0030` |
| `junction_name` | string | Real Bengaluru locality (Silk Board, Hebbal Flyover, etc.) |
| `latitude`, `longitude` | float | Real approximate coordinates |
| `number_of_roads` | int | **Derived** — graph-degree, computed from `roads` table (guaranteed accurate) |
| `junction_type` | enum | Signalized / Roundabout / Flyover / Uncontrolled |
| `priority_level` | enum | High / Medium / Low |

**Sample:**
```json
{"junction_id": "J0001", "junction_name": "Silk Board Junction", "latitude": 12.9172,
 "longitude": 77.6228, "number_of_roads": 4, "junction_type": "Signalized", "priority_level": "High"}
```
**MongoDB collection:** `junctions`
**Validation:** `number_of_roads` must equal `count(roads where junction_start=id OR junction_end=id)` — enforced at generation time.

---

## Dataset 3 — `03_traffic_signals` (26 rows — one per Signalized/Flyover/Roundabout junction)

| Column | Type | Description |
|---|---|---|
| `signal_id` **PK** | string | `S0001`... |
| `junction_id` **FK→junctions.junction_id** | string | |
| `green_time_sec` / `yellow_time_sec` / `red_time_sec` | int | Signal phase durations |
| `adaptive_mode` | bool | Whether AI-adaptive control is enabled |
| `current_status` | enum | Green / Yellow / Red |
| `last_updated` | ISO datetime | |

**Sample:**
```json
{"signal_id": "S0001", "junction_id": "J0001", "green_time_sec": 25, "yellow_time_sec": 4,
 "red_time_sec": 25, "adaptive_mode": true, "current_status": "Yellow", "last_updated": "2026-07-30T23:44:00"}
```
**MongoDB collection:** `traffic_signals`
**Validation:** `green_time_sec + yellow_time_sec + red_time_sec` = full cycle length (used by simulation engine); one signal per applicable junction (1:1).

---

## Dataset 4 — `04_vehicles` (1,000 rows)

| Column | Type | Description |
|---|---|---|
| `vehicle_id` **PK** | string | `V000001`–`V001000` |
| `vehicle_type` | enum | Car (42%) / Bike (36%) / Truck (8%) / Bus (6%) / Ambulance (4%) / Fire Truck (4%) |
| `gps_lat`, `gps_long` | float | Current position (snapped near a real road) |
| `current_speed_kmph` | float | |
| `lane` | int | 1–4 |
| `source`, `destination` **FK→junctions.junction_id** | string | Origin/destination junction |
| `priority_level` | enum | Normal / High / Emergency (Ambulance & Fire Truck = Emergency) |
| `fuel_type` | enum | Conditioned on vehicle type (bikes: Petrol/Electric/CNG; trucks: Diesel/CNG; etc.) |

**Sample:**
```json
{"vehicle_id": "V000001", "vehicle_type": "Car", "gps_lat": 12.985529, "gps_long": 77.622209,
 "current_speed_kmph": 25.2, "lane": 4, "source": "J0001", "destination": "J0013",
 "priority_level": "Normal", "fuel_type": "CNG"}
```
**MongoDB collection:** `vehicles`
**Validation:** `source != destination`; `priority_level = "Emergency"` if and only if `vehicle_type` in {Ambulance, Fire Truck}.

---

## Dataset 5 — `05_live_traffic` (3,600 rows — 50 roads × 72 hourly timestamps / 3 days)

| Column | Type | Description |
|---|---|---|
| `timestamp` | ISO datetime | Hourly, 2026-07-29T00:00 → 2026-07-31T23:00 |
| `road_id` **FK→roads.road_id** | string | |
| `vehicle_count` | int | Modeled with rush-hour (8–10am, 6–8pm) and rain-penalty factors |
| `average_speed_kmph` | float | Falls as density rises, further reduced by rain/fog |
| `density_pct` | float | 0–100, `vehicle_count / capacity` |
| `travel_time_min` | float | Derived from `length_km / average_speed_kmph` |
| `queue_length_m` | float | Rises sharply above 40% density |
| `congestion_level` | enum | Low (<25%) / Medium (<55%) / High (<80%) / Severe (≥80%) — **this exact bucketing is reused everywhere else in the pack (predictions, IoT sensors)** |

**Sample:**
```json
{"timestamp": "2026-07-29T00:00:00", "road_id": "R0001", "vehicle_count": 210,
 "average_speed_kmph": 40.2, "density_pct": 11.9, "travel_time_min": 4.4,
 "queue_length_m": 10.3, "congestion_level": "Low"}
```
**MongoDB collection:** `live_traffic` (recommend a compound index on `{road_id: 1, timestamp: -1}` for time-series queries)
**Validation:** `0 ≤ density_pct ≤ 100`; `congestion_level` must match the density bucket exactly.

---

## Dataset 6 — `06_weather` (72 rows — hourly, city-wide)

| Column | Type | Description |
|---|---|---|
| `timestamp` | ISO datetime | Same 3-day window, no `road_id` (city-wide) |
| `temperature_c` | float | Diurnal curve, ~19–29°C (Bengaluru range) |
| `humidity_pct`, `rainfall_mm`, `visibility_km`, `wind_speed_kmph` | float | |
| `weather_condition` | enum | Clear / Cloudy / Light Rain / Heavy Rain / Fog |

**Sample:**
```json
{"timestamp": "2026-07-29T00:00:00", "temperature_c": 22.0, "humidity_pct": 78.4,
 "rainfall_mm": 12.5, "visibility_km": 9.0, "wind_speed_kmph": 8.1, "weather_condition": "Light Rain"}
```
**MongoDB collection:** `weather`
**Relationship note:** no explicit FK — join to any timestamped table by nearest-hour match. `live_traffic`'s speed values were already generated with this exact weather applied (rain → lower average speed), so the correlation is real in the data, not just cosmetic.

---

## Dataset 7 — `07_emergency_vehicles` (30 rows)

| Column | Type | Description |
|---|---|---|
| `ambulance_id` **PK** | string | `AMB0001`... |
| `hospital_id` **FK→hospitals.hospital_id** | string | |
| `destination_road_id` **FK→roads.road_id** | string | |
| `priority` | enum | Critical / Standby |
| `current_location_lat/long` | float | |
| `eta_min` | float | 0 if not dispatched |
| `status` | enum | Dispatched / En Route / Arrived / Available |

**Sample:**
```json
{"ambulance_id": "AMB0001", "hospital_id": "H001", "destination_road_id": "R0005",
 "priority": "Standby", "current_location_lat": 12.963356, "current_location_long": 77.581131,
 "eta_min": 0.0, "status": "Available"}
```
**MongoDB collection:** `emergency_vehicles`
**Validation:** every `hospital_id` resolves in `hospitals`; ambulance counts per hospital match `hospitals.ambulance_count`.

---

## Dataset 8 — `08_hospitals` (15 rows)

| Column | Type | Description |
|---|---|---|
| `hospital_id` **PK** | string | `H001`–`H015` |
| `hospital_name` | string | Real Bengaluru hospitals (Victoria, NIMHANS, Manipal, Fortis, Apollo, etc.) |
| `latitude`, `longitude` | float | |
| `ambulance_count` | int | 2–6 |
| `capacity_beds` | int | 80–600 |

**Sample:**
```json
{"hospital_id": "H001", "hospital_name": "Victoria Hospital", "latitude": 12.9634,
 "longitude": 77.5772, "ambulance_count": 3, "capacity_beds": 150}
```
**MongoDB collection:** `hospitals`

---

## Dataset 9 — `09_traffic_incidents` (200 rows)

| Column | Type | Description |
|---|---|---|
| `incident_id` **PK** | string | `INC00001`... |
| `road_id` **FK→roads.road_id** | string | |
| `incident_type` | enum | Accident (35%) / Vehicle Breakdown (25%) / Construction (20%) / Tree Fall (12%) / Flood (8%) |
| `severity` | enum | Minor / Moderate / Severe / Critical |
| `start_time`, `expected_clear_time` | ISO datetime | Clear-time offset scales with severity (10 min–4 hrs) |

**Sample:**
```json
{"incident_id": "INC00001", "road_id": "R0019", "incident_type": "Accident", "severity": "Minor",
 "start_time": "2026-07-31T06:53:00", "expected_clear_time": "2026-07-31T07:10:00"}
```
**MongoDB collection:** `traffic_incidents`
**Validation:** `expected_clear_time > start_time` always.

---

## Dataset 10 — `10_traffic_cameras` (100 rows — 2 per road)

| Column | Type | Description |
|---|---|---|
| `camera_id` **PK** | string | `CAM0001`... |
| `road_id` **FK→roads.road_id** | string | |
| `camera_angle_deg` | int | 0–315 |
| `fps` | int | 15/24/30/60 |
| `resolution` | enum | 720p / 1080p / 4K |
| `status` | enum | Active (88%) / Inactive / Maintenance |

**MongoDB collection:** `traffic_cameras`

---

## Dataset 11 — `11_iot_sensors` (1,200 rows — 50 sensors × 24 hourly readings)

| Column | Type | Description |
|---|---|---|
| `sensor_id` **PK (composite with timestamp)** | string | `IOT0001`... (one sensor per road) |
| `road_id` **FK→roads.road_id** | string | |
| `timestamp` | ISO datetime | Day 1 of the simulation window |
| `traffic_density_pct`, `vehicle_count`, `average_speed_kmph` | — | **Pulled directly from `live_traffic` for the same road+hour**, so IoT and live-traffic numbers agree by construction |
| `occupancy_pct` | float | |
| `air_quality_aqi` | int | Correlated with density + rain |
| `noise_level_db` | float | Correlated with density |

**Sample:**
```json
{"sensor_id": "IOT0001", "road_id": "R0001", "timestamp": "2026-07-29T00:00:00",
 "traffic_density_pct": 11.9, "vehicle_count": 210, "average_speed_kmph": 40.2,
 "occupancy_pct": 12.0, "air_quality_aqi": 61, "noise_level_db": 58.8}
```
**MongoDB collection:** `iot_sensors`

---

## Dataset 12 — `12_public_transport` (100 rows)

| Column | Type | Description |
|---|---|---|
| `bus_id` **PK** | string | `BMTC0001`... |
| `route` | string | Real BMTC-style route codes (500D, KBS-3A, G4, Vayu Vajra V-500, etc.) |
| `current_location_lat/long` | float | |
| `current_road_id` **FK→roads.road_id** | string | |
| `occupancy_pct` | int | 10–100 |
| `eta_min` | float | |

**MongoDB collection:** `public_transport`

---

## Dataset 13 — `13_carbon_emission` (150 rows — 50 roads × 3 days)

| Column | Type | Description |
|---|---|---|
| `road_id` **FK→roads.road_id** | string | |
| `date` | date | |
| `vehicle_count` | int | Sum of that road's `live_traffic.vehicle_count` for the day |
| `fuel_consumption_l` | float | `vehicle_count × length_km × 0.09 L/km` blended fleet estimate |
| `estimated_co2_kg` | float | `fuel_consumption_l × 2.35 kg/L` blended emission factor |
| `aqi` | int | Correlated with average density that day |

**Sample:**
```json
{"road_id": "R0001", "date": "2026-07-29", "vehicle_count": 19125,
 "fuel_consumption_l": 5043.3, "estimated_co2_kg": 11851.8, "aqi": 122}
```
**MongoDB collection:** `carbon_emissions`

---

## Dataset 14 — `14_traffic_prediction` (1,200 rows — 50 roads × 24-hour forward horizon)

| Column | Type | Description |
|---|---|---|
| `prediction_id` **PK** | string | `PRED000001`... |
| `road_id` **FK→roads.road_id** | string | |
| `timestamp` | ISO datetime | Future hour being predicted (starts right after the live_traffic window ends) |
| `current_traffic_level` | enum | Snapshot at prediction time |
| `predicted_traffic_level` | enum | Low/Medium/High/Severe |
| `predicted_density_pct` | float | |
| `prediction_confidence` | float | 0.55–0.97, decays slightly with horizon distance |
| `recommended_action` | string | Auto-derived from predicted level (maps 1:1 to a lookup table — see script) |

**MongoDB collection:** `traffic_predictions`
**Validation:** `prediction_confidence` strictly decreasing in expectation as horizon (`h`) grows.

---

## Dataset 15 — `15_simulation` (60 rows)

| Column | Type | Description |
|---|---|---|
| `simulation_id` **PK** | string | `SIM0001`... |
| `scenario` | enum | Signal Timing Change / Vehicle Diversion / Emergency Corridor / Bus Priority / Heavy Vehicle Restriction / Combined Strategy |
| `road_id` **FK→roads.road_id** | string | |
| `traffic_reduction_pct`, `fuel_saved_l`, `delay_reduced_min` | float | |
| `recommendation` | string | Auto-generated summary sentence |

**MongoDB collection:** `simulations`

---

## Dataset 16 — `16_driver_recommendation` (500 rows)

| Column | Type | Description |
|---|---|---|
| `vehicle_id` **FK→vehicles.vehicle_id** | string | |
| `current_speed_kmph`, `recommended_speed_kmph` | float | |
| `next_signal_eta_sec` | int | |
| `green_wave_status` | bool | True if recommended speed keeps the vehicle within the green wave |

**MongoDB collection:** `driver_recommendations`

---

## Dataset 17 — `17_emergency_corridor` (11 rows — active dispatches only)

| Column | Type | Description |
|---|---|---|
| `corridor_id` **PK** | string | `COR0003`... |
| `ambulance_id` **FK→emergency_vehicles.ambulance_id** | string | |
| `road_id` **FK→roads.road_id** | string | |
| `priority` | string | Always "Critical" |
| `signals_modified` | int | 1–5 |
| `estimated_time_saved_min` | float | |

**Note:** intentionally smaller than `emergency_vehicles` (30) — only ambulances currently `Dispatched`/`En Route` get an active corridor record, exactly as a real system would only log corridors for active emergencies.
**MongoDB collection:** `emergency_corridors`

---

## Dataset 18 — `18_infrastructure` (50 rows — one per road)

| Column | Type | Description |
|---|---|---|
| `road_id` **FK→roads.road_id, unique** | string | |
| `has_bridge` | bool | ~25% of roads |
| `road_stress_pct` | float | Derived from `roads.road_condition` |
| `bridge_stress_pct` | float or null | Only populated when `has_bridge = true` |
| `maintenance_score` | float | Inverse of stress |
| `road_health` | enum | Good (>75) / Fair (>50) / Poor (>25) / Critical |

**Sample:**
```json
{"road_id": "R0001", "has_bridge": false, "road_stress_pct": 24.3, "bridge_stress_pct": null,
 "maintenance_score": 79.3, "road_health": "Good"}
```
**MongoDB collection:** `infrastructure`

---

## Dataset 19 — `19_ai_decision` (150 rows)

| Column | Type | Description |
|---|---|---|
| `decision_id` **PK** | string | `DEC00001`... |
| `timestamp` | ISO datetime | |
| `road_id` **FK→roads.road_id**, `junction_id` **FK→junctions.junction_id** | string | |
| `traffic_ai_recommendation` | string | One of 4 canned strategies |
| `emergency_ai_recommendation` | string | |
| `environment_ai_recommendation` | string | |
| `infrastructure_ai_recommendation` | string | |
| `public_transport_recommendation` | string | |
| `master_ai_decision` | string | **Rule-based fusion**: if the Emergency agent has an active-emergency recommendation, it always wins; otherwise Traffic AI wins unless it has nothing to do, in which case Public Transport AI wins |
| `reason` | string | Explains the priority rule that was applied — this is your "Explainable AI" feature made concrete |

**MongoDB collection:** `ai_decisions`

---

## Dataset 20 — `20_feedback` (200 rows)

| Column | Type | Description |
|---|---|---|
| `feedback_id` **PK** | string | `FB00001`... |
| `prediction_id` **FK→traffic_prediction.prediction_id** | string | |
| `road_id` **FK→roads.road_id** | string | |
| `predicted_density_pct`, `actual_density_pct` | float | |
| `difference` | float | `abs(actual - predicted)` |
| `accuracy` | float | `1 - difference/100` |
| `model_updated` | bool | True when `difference > 12` — this is your Continuous Learning trigger condition made concrete |

**MongoDB collection:** `feedback`
**This is the dataset that powers your "Continuous Learning" module** — join it back to `traffic_prediction` on `prediction_id` to build a predicted-vs-actual dashboard, and use `model_updated=true` rows as the trigger log for retraining events.

---

## Recommended MongoDB collection list (copy-paste)

```
roads, junctions, traffic_signals, vehicles, live_traffic, weather,
emergency_vehicles, hospitals, traffic_incidents, traffic_cameras,
iot_sensors, public_transport, carbon_emissions, traffic_predictions,
simulations, driver_recommendations, emergency_corridors,
infrastructure, ai_decisions, feedback
```

Suggested indexes:
- `roads.road_id`, `junctions.junction_id`, `vehicles.vehicle_id`, `hospitals.hospital_id` — unique index (they're your primary lookup keys)
- `live_traffic`, `iot_sensors`, `traffic_prediction` — compound index `{road_id: 1, timestamp: -1}` for the time-series queries your dashboard will run constantly
- `traffic_incidents` — index on `road_id` + `severity`

---

## How to extend this pack

Open `generate_twinflow_datasets.py` and edit the `CONFIG` block at the top:

```python
N_JUNCTIONS = 30        # more junctions = bigger city
N_ROADS = 50             # more roads = denser network
N_VEHICLES = 1000        # more simultaneous vehicles on the map
SIM_DAYS = 3              # more days = more live_traffic/weather/iot rows
PRED_HORIZON_HOURS = 24  # longer forward-looking prediction window
N_INCIDENTS = 200
```

Then re-run: `python3 generate_twinflow_datasets.py`. The script re-validates every foreign key
before writing anything, so if you break a relationship while editing, it will fail loudly with
a `VALIDATION ERRORS` list instead of silently producing a broken dataset.
