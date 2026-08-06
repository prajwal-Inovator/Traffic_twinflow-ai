from typing import List
from datetime import datetime
import os

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.base import BaseRepository
from ..models.prediction import Prediction
from ..core.exceptions import NotFoundError


class PredictionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = BaseRepository[Prediction](
            db,
            "predictions",
            Prediction
        )

        self.ai_service_url = os.getenv(
            "AI_SERVICE_URL",
            "http://localhost:8001"
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

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.ai_service_url}/predict",
                json=current_data,
            )

        if response.status_code != 200:
            raise NotFoundError(
                f"AI Service returned {response.status_code}"
            )

        pred = response.json()

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