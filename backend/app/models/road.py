# backend/app/models/road.py
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class RoadSegment(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    start_junction_id: str
    end_junction_id: str
    length: float  # meters
    lanes: int
    speed_limit: float  # km/h
    geometry: List[List[float]]  # [[lng, lat], ...] for polyline
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True