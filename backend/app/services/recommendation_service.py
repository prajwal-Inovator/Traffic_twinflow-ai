# backend/app/services/recommendation_service.py
from typing import Dict, Any, Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...ai.recommendation.speed_recommender import SpeedRecommender
from ...ai.recommendation.lane_recommender import LaneRecommender
from ...ai.recommendation.departure_optimizer import DepartureOptimizer
from ...ai.recommendation.savings_calculator import SavingsCalculator
from ..repositories.base import BaseRepository
from ..models.recommendation import SpeedRecommendation
from datetime import datetime
import logging
from recommendation_engine.recommender import AdaptiveVelocityRecommender
from recommendation_engine.models import RecommendationRequest

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.speed_recommender = SpeedRecommender()
        self.lane_recommender = LaneRecommender()
        self.departure_optimizer = DepartureOptimizer()
        self.savings_calculator = SavingsCalculator()
        self.repo = BaseRepository[SpeedRecommendation](db, "speed_recommendations", SpeedRecommendation)
        self.recommender = AdaptiveVelocityRecommender(
            prediction_service=PredictionService(db),  # we need to inject
            traffic_service=TrafficService(db),
        )

    async def get_recommendation(
        self,
        junction_id: str,
        road_id: Optional[str] = None,
        vehicle_type: str = "car",
        distance_km: float = 5.0,
    ) -> Dict[str, Any]:
        """
        Generate a complete recommendation for a driver/vehicle.
        """
        # Fetch current traffic data for the junction/road
        # For now, we'll simulate or fetch from DB.
        # We'll use some placeholder values.
        current_data = {
            "speed_limit": 50,
            "current_speed": 35,
            "congestion_level": 60,
            "emergency_vehicle": False,
            "bus_priority": False,
            "weather": "clear",
            "time_of_day": datetime.now().hour,
            "lane_data": [
                {"lane_index": 0, "vehicle_count": 15, "queue_length": 10, "avg_speed": 30},
                {"lane_index": 1, "vehicle_count": 20, "queue_length": 15, "avg_speed": 25},
                {"lane_index": 2, "vehicle_count": 10, "queue_length": 5, "avg_speed": 40},
            ],
        }

        # Speed recommendation
        speed_rec = self.speed_recommender.recommend(
            road_id=road_id or junction_id,
            speed_limit=current_data["speed_limit"],
            current_speed=current_data["current_speed"],
            congestion_level=current_data["congestion_level"],
            emergency_vehicle=current_data["emergency_vehicle"],
            bus_priority=current_data["bus_priority"],
            weather=current_data["weather"],
            time_of_day=current_data["time_of_day"],
        )

        # Lane recommendation
        lane_rec = self.lane_recommender.recommend(
            road_id=road_id or junction_id,
            lane_data=current_data["lane_data"],
            destination_lane=None,
        )

        # Departure time optimization (using heuristic or prediction)
        dept_opt = self.departure_optimizer.optimize(
            route_id=road_id or junction_id,
            current_time=datetime.now(),
            allowed_window=60,
        )

        # Savings
        baseline_speed = current_data["current_speed"]
        recommended_speed = speed_rec["recommended_speed"]
        savings = self.savings_calculator.calculate(
            vehicle_type=vehicle_type,
            distance_km=distance_km,
            recommended_speed=recommended_speed,
            baseline_speed=baseline_speed,
        )

        # Combine into final recommendation
        recommendation = {
            "junction_id": junction_id,
            "road_id": road_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "speed": speed_rec,
            "lane": lane_rec,
            "departure": dept_opt,
            "savings": savings,
            "expected_delay": dept_opt.get("expected_delay", 0),
        }

        # Store in DB
        await self.repo.create({
            "junction_id": junction_id,
            "optimal_speed": speed_rec["recommended_speed"],
            "optimal_lane": lane_rec["optimal_lane"],
            "departure_time": datetime.fromisoformat(dept_opt["optimal_departure_time"]),
            "expected_delay": dept_opt.get("expected_delay", 0),
            "fuel_saved": savings["fuel_saved_liters"],
            "co2_saved": savings["co2_saved_kg"],
            "created_at": datetime.utcnow(),
        })

        return recommendation
    
    async def get_recommendation_for_junction(self, junction_id: str, user_context: dict = None) -> SpeedRecommendation:
        """Legacy: get speed recommendation."""
        # We'll use the new recommender for full recommendation.
        request = RecommendationRequest(junction_id=junction_id, **user_context or {})
        full_rec = await self.recommender.get_recommendations(request)
        # Convert to old format if needed
        return full_rec.speed

    async def get_full_recommendation(self, request: RecommendationRequest) -> AdaptiveVelocityRecommendation:
        """Get full adaptive velocity recommendation."""
        return await self.recommender.get_recommendations(request)