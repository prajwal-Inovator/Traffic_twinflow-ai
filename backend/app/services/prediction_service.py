from typing import List
from datetime import datetime
import os

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.base import BaseRepository
from ..models.prediction import Prediction
from ..core.exceptions import TwinFlowException
from .http_client import ServiceClient


class PredictionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = BaseRepository[Prediction](
            db,
            "predictions",
            Prediction,
        )

        self.ai_service_url = os.getenv(
            "AI_SERVICE_URL",
            "http://localhost:8001",
        )
        self.client = ServiceClient(
            self.ai_service_url,
            timeout=60,
            service_name="AI Service",
        )

    async def get_predictions_for_junction(
        self,
        junction_id: str,
        horizon: int = 30,
    ) -> List[Prediction]:

        current_data = {
            "junction_id": junction_id,
            "hour": datetime.utcnow().hour,
            "day_of_week": datetime.utcnow().weekday(),
            "vehicle_count": 25,
            "queue_length": 10,
            "occupancy": 0.5,
            "avg_speed": 30,
            "horizon": horizon,
        }

        pred = await self.client.request(
            "POST",
            "/predict",
            json=current_data,
        )

        pred_doc = {
            "junction_id": junction_id,
            "timestamp": datetime.utcnow(),
            "horizon_minutes": horizon,
            "congestion_level": pred.get("congestion_level"),
            "predicted_vehicle_count": pred.get("vehicle_count"),
            "confidence": pred.get("confidence"),
            "model_version": pred.get("model_version", "v1"),
            "features": pred.get("explanation", {}),
        }

        saved = await self.repo.create(pred_doc)
        return [saved]

    async def save_prediction(self, prediction_data: dict) -> Prediction:
        return await self.repo.create(prediction_data)
