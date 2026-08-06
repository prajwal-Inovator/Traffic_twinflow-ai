from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    junction_id: str
    vehicle_type: str = "car"
    current_location_lat: Optional[float] = None
    current_location_lng: Optional[float] = None
    destination_lat: Optional[float] = None
    destination_lng: Optional[float] = None
    desired_departure_time: Optional[datetime] = None
    acceptable_delay: float = 5.0


class AdaptiveVelocityRecommendation(BaseModel):
    junction_id: str
    timestamp: Optional[datetime] = None
    speed: Optional[Dict[str, Any]] = None
    lane: Optional[Dict[str, Any]] = None
    departure: Optional[Dict[str, Any]] = None
    fuel_saved_liters: Optional[float] = 0.0
    co2_saved_kg: Optional[float] = 0.0
    expected_delay_minutes: Optional[float] = 0.0
    overall_confidence: Optional[float] = 0.0
    explanation: Optional[str] = ""
