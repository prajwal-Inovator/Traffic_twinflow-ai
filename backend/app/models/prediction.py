# backend/app/models/prediction.py
from typing import Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class Prediction(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    junction_id: str
    timestamp: datetime  # prediction time
    horizon_minutes: int  # 5, 10, 20, 30
    congestion_level: float  # 0-100
    predicted_vehicle_count: int
    confidence: float  # 0-1
    model_version: str
    features: Dict[str, float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True