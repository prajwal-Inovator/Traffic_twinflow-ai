# negotiation_engine/negotiation_protocol.py
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class JunctionState(BaseModel):
    """State of a junction used in negotiation."""
    junction_id: str
    vehicle_count: int
    queue_length: int
    signal_phase: str  # "red", "yellow", "green"
    predicted_vehicles: int  # next interval
    emergency_status: bool
    bus_priority: bool
    pollution: float  # AQI or CO2 index
    weather: str      # "clear", "rain", "fog", "snow"
    current_delay: float  # seconds
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class NeighborState(BaseModel):
    """State of a neighboring junction."""
    junction_id: str
    state: JunctionState
    distance: float  # meters (or travel time)

class MasterRecommendation(BaseModel):
    """Recommendation from Master Agent."""
    junction_id: str
    green_time: int  # seconds
    red_time: int    # seconds
    priority: float  # 0-1 (higher = more critical)
    confidence: float  # 0-1
    reason: str       # human-readable explanation
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class NegotiationMessage(BaseModel):
    """Message exchanged between agents and master."""
    type: str  # "state_update", "recommendation", "ack", "error"
    sender_id: str
    recipient_id: Optional[str] = None  # None for broadcast
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)