# backend/app/models/carbon_report.py
from typing import Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class CarbonReport(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    junction_id: str
    date: datetime
    co2_emissions: float  # kg
    fuel_consumption: float  # liters
    co2_saved: float  # kg (due to optimization)
    fuel_saved: float  # liters
    baseline_co2: float
    baseline_fuel: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True