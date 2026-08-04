# backend/app/api/v1/endpoints/emergency.py
from fastapi import APIRouter, Depends
from ....api.deps import get_db
from ....services.emergency_service import EmergencyService

router = APIRouter()

@router.get("/active")
async def get_active_emergencies(db=Depends(get_db)):
    service = EmergencyService(db)
    incidents = await service.get_active_emergencies()
    return {"success": True, "data": incidents}

@router.post("/corridor/{incident_id}")
async def activate_corridor(incident_id: str, db=Depends(get_db)):
    service = EmergencyService(db)
    result = await service.create_emergency_corridor(incident_id)
    return {"success": True, "data": result}