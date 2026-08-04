# backend/app/models/vehicle.py
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class VehicleType(str, Enum):
    CAR = "car"
    BUS = "bus"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"
    EMERGENCY = "emergency"

class Vehicle(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    external_id: str  # Original ID from dataset or SUMO
    type: VehicleType
    speed: float  # km/h
    heading: float  # degrees
    lat: float
    lng: float
    junction_id: Optional[str] = None
    lane: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True