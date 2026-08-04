# ai/recommendation/recommendation_engine.py
import logging
from typing import Dict, Any, Optional, List
from .speed_recommender import SpeedRecommender
from .lane_recommender import LaneRecommender
from .departure_optimizer import DepartureTimeOptimizer

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    Orchestrates all recommendations: speed, lane, departure time.
    Integrates data from digital twin, predictions, and negotiation.
    """

    def __init__(self):
        self.speed_rec = SpeedRecommender()
        self.lane_rec = LaneRecommender()
        self.departure_rec = DepartureTimeOptimizer()

    def get_full_recommendation(
        self,
        junction_id: str,
        current_data: Dict[str, Any],
        prediction: Dict[str, Any],
        signal_timing: Dict[str, Any],
        target_arrival: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get comprehensive recommendation for a junction/vehicle.
        """
        # Speed recommendation
        speed = self.speed_rec.recommend(junction_id, current_data, prediction, signal_timing)

        # Lane recommendation
        lane = self.lane_rec.recommend(junction_id, current_data)

        # Departure time optimization
        target_dt = datetime.fromisoformat(target_arrival) if target_arrival else None
        departure = self.departure_rec.recommend(
            junction_id, current_data, prediction, target_dt
        )

        # Combine
        return {
            "junction_id": junction_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "speed": speed,
            "lane": lane,
            "departure": departure,
            "summary": {
                "optimal_speed": speed["optimal_speed"],
                "optimal_lane": lane["optimal_lane"],
                "recommended_departure": departure["recommended_departure"],
                "fuel_saved": departure["fuel_saved_liters"] + (lane.get("fuel_saving_estimate", 0) / 100),
                "co2_saved": departure["co2_saved_kg"] + (lane.get("fuel_saving_estimate", 0) / 100 * 2.31),
                "expected_delay_reduction": speed["expected_delay_reduction"],
            }
        }