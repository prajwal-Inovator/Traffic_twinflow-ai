# backend/tests/unit/test_prediction_service.py
import pytest
from app.services.prediction_service import PredictionService
from datetime import datetime

@pytest.mark.asyncio
async def test_save_and_get_prediction(db_client):
    service = PredictionService(db_client)
    pred_data = {
        "junction_id": "junction_1",
        "timestamp": datetime.utcnow(),
        "horizon_minutes": 30,
        "congestion_level": 65.5,
        "predicted_vehicle_count": 45,
        "confidence": 0.85,
        "model_version": "v1",
        "features": {"vehicle_count": 20, "queue_length": 10}
    }
    saved = await service.save_prediction(pred_data)
    assert saved.id is not None
    fetched = await service.get_predictions_for_junction("junction_1")
    assert len(fetched) == 1
    assert fetched[0].congestion_level == 65.5