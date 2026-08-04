# backend/app/models/simulation_result.py
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class SimulationResult(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    simulation_id: str
    junction_id: str
    time_horizon: int  # minutes (5,10,20,30)
    predicted_congestion: float
    affected_junctions: List[str]
    propagation_strength: float
    data: Dict = Field(default_factory=dict)  # additional metrics
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True