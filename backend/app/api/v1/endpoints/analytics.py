# backend/app/api/v1/endpoints/analytics.py
from fastapi import APIRouter, Depends
from ....api.deps import get_db
from ....services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_metrics(db=Depends(get_db)):
    service = AnalyticsService(db)
    metrics = await service.get_dashboard_metrics()
    return {"success": True, "data": metrics}