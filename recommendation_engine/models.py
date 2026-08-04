# recommendation_engine/models.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class RecommendationRequest(BaseModel):
    junction_id: str
    vehicle_type: str = "car"  # car, bus, truck, motorcycle, emergency
    current_location_lat: Optional[float] = None
    current_location_lng: Optional[float] = None
    destination_lat: Optional[float] = None
    destination_lng: Optional[float] = None
    desired_departure_time: Optional[datetime] = None
    acceptable_delay: float = 5  # minutes

class SpeedRecommendation(BaseModel):
    junction_id: str
    optimal_speed: float  # km/h
    current_speed: Optional[float] = None
    speed_limit: Optional[float] = None
    reason: str
    confidence: float  # 0-1

class LaneRecommendation(BaseModel):
    junction_id: str
    optimal_lane: int  # 0-indexed
    lane_occupancy: Dict[int, float]  # lane -> occupancy
    reason: str
    confidence: float

class DepartureRecommendation(BaseModel):
    junction_id: str
    suggested_departure_time: datetime
    original_departure_time: Optional[datetime] = None
    expected_delay_if_now: float  # minutes
    expected_delay_if_later: float  # minutes
    reason: str
    confidence: float

class AdaptiveVelocityRecommendation(BaseModel):
    """Combined recommendation for a user."""
    junction_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    speed: Optional[SpeedRecommendation] = None
    lane: Optional[LaneRecommendation] = None
    departure: Optional[DepartureRecommendation] = None
    fuel_saved_liters: float = 0.0
    co2_saved_kg: float = 0.0
    expected_delay_minutes: float = 0.0
    overall_confidence: float = 0.0
    explanation: str = ""