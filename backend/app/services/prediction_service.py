# backend/app/services/prediction_service.py
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..repositories.base import BaseRepository
from ..models.prediction import Prediction
from ..core.exceptions import NotFoundError
from ai.prediction.traffic_predictor import TrafficPredictor

class PredictionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = BaseRepository[Prediction](db, "predictions", Prediction)
        self.predictor = TrafficPredictor()
        self.predictor.load_models()

    async def get_predictions_for_junction(self, junction_id: str, horizon: int = 30) -> List[Prediction]:
        # Fetch current data from DB (vehicles, signals, etc.)
        # For now, we'll generate synthetic current data
        current_data = {
            'hour': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'vehicle_count': 25,
            'queue_length': 10,
            'occupancy': 0.5,
            'avg_speed': 30,
        }
        # Get prediction
        pred = self.predictor.predict_congestion(junction_id, current_data, horizon)
        # Store in DB
        pred_doc = {
            "junction_id": junction_id,
            "timestamp": datetime.utcnow(),
            "horizon_minutes": horizon,
            "congestion_level": pred['congestion_level'],
            "predicted_vehicle_count": pred['vehicle_count'],
            "confidence": pred['confidence'],
            "model_version": "v1",
            "features": pred.get('explanation', {}),
        }
        saved = await self.repo.create(pred_doc)
        return [saved]

