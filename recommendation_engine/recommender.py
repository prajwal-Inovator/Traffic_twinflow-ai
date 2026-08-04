# recommendation_engine/recommender.py
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np
from .models import (
    RecommendationRequest,
    SpeedRecommendation,
    LaneRecommendation,
    DepartureRecommendation,
    AdaptiveVelocityRecommendation,
)
from .optimizers import SpeedOptimizer, LaneOptimizer, DepartureOptimizer

logger = logging.getLogger(__name__)

class AdaptiveVelocityRecommender:
    """
    Main recommendation engine that provides speed, lane, and departure recommendations
    based on live traffic data, predictions, and user context.
    """

    def __init__(self, prediction_service=None, traffic_service=None):
        self.prediction_service = prediction_service
        self.traffic_service = traffic_service
        self.speed_optimizer = SpeedOptimizer()
        self.lane_optimizer = LaneOptimizer()
        self.departure_optimizer = DepartureOptimizer()

    async def get_recommendations(self, request: RecommendationRequest) -> AdaptiveVelocityRecommendation:
        """
        Generate all recommendations for a junction based on the request.
        """
        junction_id = request.junction_id

        # Get current traffic data
        current_data = await self._get_junction_data(junction_id)
        if not current_data:
            logger.warning(f"No data for junction {junction_id}, returning default")
            return self._default_recommendation(junction_id)

        # Get congestion forecast (from prediction service)
        forecast = await self._get_congestion_forecast(junction_id)

        # Compute speed recommendation
        speed_rec = self._recommend_speed(current_data, request.vehicle_type)

        # Compute lane recommendation
        lane_rec = self._recommend_lane(current_data)

        # Compute departure recommendation
        departure_rec = self._recommend_departure(
            current_data.get('congestion_level', 50),
            forecast,
            request.desired_departure_time
        )

        # Compute fuel and CO2 savings
        fuel_saved, co2_saved = self._estimate_savings(speed_rec, lane_rec, current_data)

        # Overall confidence
        overall_conf = np.mean([speed_rec.confidence, lane_rec.confidence, departure_rec.confidence])

        explanation = self._generate_explanation(speed_rec, lane_rec, departure_rec)

        return AdaptiveVelocityRecommendation(
            junction_id=junction_id,
            speed=speed_rec,
            lane=lane_rec,
            departure=departure_rec,
            fuel_saved_liters=fuel_saved,
            co2_saved_kg=co2_saved,
            expected_delay_minutes=departure_rec.expected_delay_if_now if departure_rec else 0,
            overall_confidence=round(overall_conf, 2),
            explanation=explanation,
        )

    async def _get_junction_data(self, junction_id: str) -> Dict[str, Any]:
        """Fetch current traffic data for a junction."""
        if self.traffic_service:
            # Call traffic service to get live data
            # For now, we mock
            pass
        # Mock data
        return {
            'congestion_level': np.random.uniform(20, 80),
            'current_speed': np.random.uniform(20, 60),
            'speed_limit': 50,
            'lane_occupancy': {0: 0.3, 1: 0.6, 2: 0.4},
            'vehicle_count': np.random.randint(10, 40),
            'queue_length': np.random.randint(0, 20),
        }

    async def _get_congestion_forecast(self, junction_id: str) -> Dict[datetime, float]:
        """Get forecast from prediction service."""
        if self.prediction_service:
            # Call prediction service
            pass
        # Mock forecast
        now = datetime.now()
        return {now + timedelta(minutes=i*5): np.random.uniform(10, 80) for i in range(6)}

    def _recommend_speed(self, data: Dict, vehicle_type: str) -> SpeedRecommendation:
        congestion = data.get('congestion_level', 50)
        current_speed = data.get('current_speed')
        speed_limit = data.get('speed_limit', 60)
        opt_speed, reason, conf = SpeedOptimizer.optimize(congestion, current_speed, speed_limit, vehicle_type)
        return SpeedRecommendation(
            junction_id=data.get('junction_id', 'unknown'),
            optimal_speed=opt_speed,
            current_speed=current_speed,
            speed_limit=speed_limit,
            reason=reason,
            confidence=conf,
        )

    def _recommend_lane(self, data: Dict) -> LaneRecommendation:
        lane_occ = data.get('lane_occupancy', {})
        opt_lane, occ, reason, conf = LaneOptimizer.optimize(lane_occ)
        return LaneRecommendation(
            junction_id=data.get('junction_id', 'unknown'),
            optimal_lane=opt_lane,
            lane_occupancy=occ,
            reason=reason,
            confidence=conf,
        )

    def _recommend_departure(self, current_cong: float, forecast: Dict, desired: Optional[datetime]) -> DepartureRecommendation:
        best_time, delay_now, delay_later, reason, conf = DepartureOptimizer.optimize(
            current_cong, forecast, desired
        )
        return DepartureRecommendation(
            junction_id='unknown',
            suggested_departure_time=best_time,
            original_departure_time=desired,
            expected_delay_if_now=delay_now,
            expected_delay_if_later=delay_later,
            reason=reason,
            confidence=conf,
        )

    def _estimate_savings(self, speed_rec: SpeedRecommendation, lane_rec: LaneRecommendation, data: Dict) -> Tuple[float, float]:
        """Estimate fuel and CO2 savings based on recommendations."""
        # Simplified: better speed and lane choice reduce fuel by 5-15%
        base_fuel = 8.0  # liters per 100 km
        base_co2 = 18.4  # kg CO2 per 100 km (petrol)
        # Improvement from speed
        speed_improve = 0.1 if speed_rec.optimal_speed > 40 else 0.05
        # Improvement from lane (lower occupancy -> less stop-and-go)
        lane_improve = 0.05 if lane_rec.optimal_lane is not None else 0.0
        total_improve = speed_improve + lane_improve
        # Assume trip distance 10 km
        distance_km = 10
        fuel_saved = base_fuel * distance_km / 100 * total_improve
        co2_saved = base_co2 * distance_km / 100 * total_improve
        return round(fuel_saved, 2), round(co2_saved, 2)

    def _generate_explanation(self, speed_rec: SpeedRecommendation, lane_rec: LaneRecommendation, dep_rec: DepartureRecommendation) -> str:
        parts = []
        if speed_rec:
            parts.append(f"Drive at {speed_rec.optimal_speed} km/h ({speed_rec.reason})")
        if lane_rec:
            parts.append(f"Use lane {lane_rec.optimal_lane} ({lane_rec.reason})")
        if dep_rec:
            parts.append(f"Depart at {dep_rec.suggested_departure_time.strftime('%H:%M')} ({dep_rec.reason})")
        return ". ".join(parts) if parts else "No recommendations available."

    def _default_recommendation(self, junction_id: str) -> AdaptiveVelocityRecommendation:
        return AdaptiveVelocityRecommendation(
            junction_id=junction_id,
            speed=SpeedRecommendation(junction_id=junction_id, optimal_speed=40, reason="Default", confidence=0.5),
            lane=LaneRecommendation(junction_id=junction_id, optimal_lane=0, lane_occupancy={0:0.5}, reason="Default", confidence=0.5),
            departure=DepartureRecommendation(junction_id=junction_id, suggested_departure_time=datetime.now(), expected_delay_if_now=5, expected_delay_if_later=5, reason="Default", confidence=0.5),
            fuel_saved_liters=0,
            co2_saved_kg=0,
            expected_delay_minutes=5,
            overall_confidence=0.5,
            explanation="No data; using defaults.",
        )