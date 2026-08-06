# backend/app/api/v1/endpoints/traffic.py
from fastapi import APIRouter, Depends, Query
from ....api.deps import get_db, get_current_active_user
from ....services.traffic_service import TrafficService
from ....models.vehicle import Vehicle
from ....models.incident import Incident
from typing import List, Optional

router = APIRouter()

@router.get("/live")
async def get_live_traffic(db=Depends(get_db)):
    service = TrafficService(db)
    data = await service.get_live_traffic()
    return {"success": True, "data": data}

@router.get("/vehicles")
async def get_vehicles(junction_id: Optional[str] = None, db=Depends(get_db)):
    service = TrafficService(db)
    if junction_id:
        vehicles = await service.get_vehicles_by_junction(junction_id)
    else:
        vehicles = await service.vehicle_repo.get_recent()
    return {"success": True, "data": vehicles}

@router.post("/incidents")
async def create_incident(incident_data: dict, db=Depends(get_db)):
    service = TrafficService(db)
    incident = await service.create_incident(incident_data)
    return {"success": True, "data": incident}

@router.put("/incidents/{incident_id}/resolve")
async def resolve_incident(incident_id: str, db=Depends(get_db)):
    service = TrafficService(db)
    incident = await service.resolve_incident(incident_id)
    return {"success": True, "data": incident}