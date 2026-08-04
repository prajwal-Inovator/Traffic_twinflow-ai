# backend/app/api/v1/endpoints/negotiation.py
from fastapi import APIRouter, Depends, Query
from ....api.deps import get_db
from ....services.negotiation_service import NegotiationService
from typing import Optional

router = APIRouter()

@router.get("/recommendations")
async def get_recommendations(junction_id: Optional[str] = None, db=Depends(get_db)):
    service = NegotiationService(db)
    recs = await service.get_recommendations(junction_id)
    return {"success": True, "data": recs}

@router.post("/trigger/{junction_id}")
async def trigger_negotiation(junction_id: str, db=Depends(get_db)):
    service = NegotiationService(db)
    result = await service.trigger_negotiation(junction_id)
    return {"success": True, "data": result}