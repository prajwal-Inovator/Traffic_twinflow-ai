# backend/app/models/signal.py
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class SignalPhase(str, Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"

class Signal(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    junction_id: str
    phase: SignalPhase
    green_time: int  # seconds
    red_time: int    # seconds
    cycle_time: int  # total cycle time
    emergency_override: bool = False
    bus_priority: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True