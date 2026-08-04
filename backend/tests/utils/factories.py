# backend/tests/utils/factories.py
from app.models.vehicle import Vehicle, VehicleType
from app.models.signal import Signal, SignalPhase
from datetime import datetime

def create_vehicle(junction_id="junction_1"):
    return Vehicle(
        external_id="veh_123",
        type=VehicleType.CAR,
        speed=45.5,
        heading=90.0,
        lat=28.6139,
        lng=77.2090,
        junction_id=junction_id,
        lane=1,
        timestamp=datetime.utcnow()
    )

def create_signal(junction_id="junction_1"):
    return Signal(
        junction_id=junction_id,
        phase=SignalPhase.GREEN,
        green_time=30,
        red_time=30,
        cycle_time=60,
        timestamp=datetime.utcnow()
    )