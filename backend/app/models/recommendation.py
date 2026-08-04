# backend/app/models/recommendation.py
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SpeedRecommendation(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    junction_id: str
    optimal_speed: float  # km/h
    optimal_lane: int
    departure_time: datetime
    expected_delay: float  # seconds
    fuel_saved: float  # liters
    co2_saved: float  # kg
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True