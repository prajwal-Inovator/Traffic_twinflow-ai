# backend/app/api/v1/endpoints/carbon.py
from fastapi import APIRouter, Depends, Query
from ....api.deps import get_db
from ....services.carbon_service import CarbonService
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.get("/report")
async def get_carbon_report(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db=Depends(get_db)
):
    service = CarbonService(db)
    from_dt = datetime.fromisoformat(from_date) if from_date else None
    to_dt = datetime.fromisoformat(to_date) if to_date else None
    reports = await service.get_reports(from_dt, to_dt)
    return {"success": True, "data": reports}