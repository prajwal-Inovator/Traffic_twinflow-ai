# backend/app/models/negotiation.py
from typing import Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class JunctionState(BaseModel):
    vehicle_count: int
    queue_length: int
    signal_phase: str  # red/yellow/green
    predicted_vehicles: int
    emergency_status: bool
    bus_priority: bool
    pollution: float
    weather: str
    current_delay: float

class NegotiationMessage(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    junction_id: str
    timestamp: datetime
    data: JunctionState

class MasterRecommendation(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    junction_id: str
    green_time: int
    red_time: int
    priority: float  # 0-1
    confidence: float  # 0-1
    reason: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True