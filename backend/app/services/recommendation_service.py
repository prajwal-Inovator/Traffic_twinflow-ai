import os
from typing import Dict, Any, Optional
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.base import BaseRepository
from ..models.recommendation import SpeedRecommendation
from ..models.recommendation_models import RecommendationRequest
from .http_client import ServiceClient


class RecommendationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = BaseRepository[SpeedRecommendation](
            db,
            "speed_recommendations",
            SpeedRecommendation,
        )
        self.recommendation_url = os.getenv(
            "RECOMMENDATION_SERVICE_URL",
            "http://localhost:8004",
        )
        self.client = ServiceClient(
            self.recommendation_url,
            timeout=60,
            service_name="Recommendation Service",
        )

    async def get_recommendation(
        self,
        junction_id: str,
        road_id: Optional[str] = None,
        vehicle_type: str = "car",
        distance_km: float = 5.0,
    ) -> Dict[str, Any]:
        params = {
            "junction_id": junction_id,
            "road_id": road_id,
            "vehicle_type": vehicle_type,
            "distance_km": distance_km,
        }

        recommendation = await self.client.request(
            "GET",
            "/recommendation",
            params={k: v for k, v in params.items() if v is not None},
        )

        speed_data = recommendation.get("speed", {})
        lane_data = recommendation.get("lane", {})
        departure_data = recommendation.get("departure", {})

        if speed_data and lane_data and departure_data:
            try:
                await self.repo.create(
                    {
                        "junction_id": junction_id,
                        "optimal_speed": speed_data.get("recommended_speed", 0),
                        "optimal_lane": lane_data.get("optimal_lane", 0),
                        "departure_time": datetime.fromisoformat(
                            departure_data.get("optimal_departure_time")
                        ) if departure_data.get("optimal_departure_time") else datetime.utcnow(),
                        "expected_delay": departure_data.get("expected_delay", 0),
                        "fuel_saved": recommendation.get("fuel_saved_liters", 0.0),
                        "co2_saved": recommendation.get("co2_saved_kg", 0.0),
                        "created_at": datetime.utcnow(),
                    }
                )
            except Exception:
                pass

        return recommendation

    async def get_recommendation_for_junction(
        self,
        junction_id: str,
        user_context: dict = None,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "GET",
            f"/recommendation/{junction_id}",
            params=user_context or {},
        )

    async def get_full_recommendation(
        self,
        request: RecommendationRequest,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/recommendation/full",
            json=request.dict(exclude_none=True),
        )
