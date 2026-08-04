# backend/app/models/incident.py
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class IncidentType(str, Enum):
    ACCIDENT = "accident"
    ROADWORK = "roadwork"
    HAZARD = "hazard"
    CONGESTION = "congestion"

class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Incident(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    type: IncidentType
    severity: IncidentSeverity
    lat: float
    lng: float
    description: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    resolved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True