# backend/app/api/v1/endpoints/recommendation.py
from fastapi import APIRouter, Depends, Query
from ....api.deps import get_db, get_current_active_user
from ....services.recommendation_service import RecommendationService
from typing import Optional
from recommendation_engine.models import RecommendationRequest

router = APIRouter()

@router.get("/")
async def get_recommendation(
    junction_id: str,
    road_id: Optional[str] = None,
    vehicle_type: str = "car",
    distance_km: float = 5.0,
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Get a recommendation for a driver."""
    service = RecommendationService(db)
    rec = await service.get_recommendation(junction_id, road_id, vehicle_type, distance_km)
    return {"success": True, "data": rec}

@router.get("/driver/{driver_id}")
async def get_driver_recommendation(
    driver_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Get recommendations for a specific driver's route."""
    # In production, we would fetch driver's route and preferences.
    # For now, we'll just return a general recommendation for a default junction.
    service = RecommendationService(db)
    rec = await service.get_recommendation("junction_1", vehicle_type="car", distance_km=5.0)
    return {"success": True, "data": rec}

@router.post("/full")
async def get_full_recommendation(
    request: RecommendationRequest,
    db=Depends(get_db)
):
    service = RecommendationService(db)
    rec = await service.get_full_recommendation(request)
    return {"success": True, "data": rec}

@router.get("/{junction_id}")
async def get_recommendation(junction_id: str, db=Depends(get_db)):
    service = RecommendationService(db)
    rec = await service.get_recommendation_for_junction(junction_id)
    return {"success": True, "data": rec}