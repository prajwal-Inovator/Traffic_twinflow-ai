# backend/app/api/v1/endpoints/prediction.py
from fastapi import APIRouter, Depends, Query
from ....api.deps import get_db
from ....services.prediction_service import PredictionService
from typing import Optional

router = APIRouter()

@router.get("/{junction_id}")
async def get_predictions(
    junction_id: str,
    horizon: Optional[int] = Query(None, ge=5, le=60),
    db=Depends(get_db)
):
    service = PredictionService(db)
    predictions = await service.get_predictions_for_junction(junction_id, horizon)
    return {"success": True, "data": predictions}

@router.post("/")
async def save_prediction(prediction_data: dict, db=Depends(get_db)):
    service = PredictionService(db)
    pred = await service.save_prediction(prediction_data)
    return {"success": True, "data": pred}