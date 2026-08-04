# recommendation_engine/optimizers.py
import numpy as np
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SpeedOptimizer:
    """Optimize speed based on traffic conditions and fuel efficiency."""

    @staticmethod
    def optimize(
        congestion_level: float,  # 0-100
        current_speed: Optional[float] = None,
        speed_limit: Optional[float] = 60,
        vehicle_type: str = "car",
    ) -> Tuple[float, str, float]:
        """
        Returns: (optimal_speed, reason, confidence)
        """
        # Optimal speed for fuel efficiency is around 40-60 km/h
        # But we also want to reduce congestion, so we recommend speed based on flow.
        if congestion_level > 80:
            # Severe congestion: recommend slow speed to avoid stop-and-go
            optimal = max(10, 30 - (congestion_level - 80) * 0.5)
            reason = "Severe congestion; reduce speed to maintain flow"
            confidence = 0.9
        elif congestion_level > 50:
            # Moderate congestion: recommend speed to match flow
            optimal = max(20, 50 - (congestion_level - 50) * 0.3)
            reason = "Moderate congestion; adjust speed for smooth flow"
            confidence = 0.8
        else:
            # Free flow: recommend optimal fuel-efficient speed
            optimal = min(speed_limit or 60, 50 + (speed_limit or 60) * 0.1)
            reason = "Light traffic; maintain fuel-efficient speed"
            confidence = 0.7

        # Clamp to reasonable range
        optimal = max(5, min(speed_limit or 60, optimal))
        return round(optimal, 1), reason, round(confidence, 2)

class LaneOptimizer:
    """Recommend optimal lane based on lane occupancy and turning intentions."""

    @staticmethod
    def optimize(
        lane_data: Dict[int, float],  # lane index -> occupancy (0-1)
        turning_intent: Optional[str] = None,  # "left", "right", "straight"
    ) -> Tuple[int, Dict[int, float], str, float]:
        """
        Returns: (optimal_lane, lane_occupancy, reason, confidence)
        """
        if not lane_data:
            return 0, {}, "No lane data available", 0.0

        # If turning, prefer lane that allows turn
        if turning_intent == "left":
            # Typically leftmost lane
            preferred = min(lane_data.keys())
        elif turning_intent == "right":
            preferred = max(lane_data.keys())
        else:
            preferred = None

        # Find lane with lowest occupancy, preferring preferred if exists
        if preferred is not None and preferred in lane_data:
            # Check if occupancy is not too high ( < 0.7)
            if lane_data[preferred] < 0.7:
                optimal = preferred
                reason = f"Preferred lane for {turning_intent} turn with low occupancy"
                confidence = 0.9
            else:
                # Find best among all
                optimal = min(lane_data, key=lambda k: lane_data[k])
                reason = f"{turning_intent} turn lane crowded; using next best"
                confidence = 0.7
        else:
            optimal = min(lane_data, key=lambda k: lane_data[k])
            reason = "Lowest occupancy lane"
            confidence = 0.8

        return optimal, lane_data, reason, round(confidence, 2)

class DepartureOptimizer:
    """Suggest optimal departure time based on congestion forecast."""

    @staticmethod
    def optimize(
        current_congestion: float,
        forecast: Dict[datetime, float],  # timestamp -> congestion level
        desired_departure: Optional[datetime] = None,
        max_delay: float = 10,  # minutes
    ) -> Tuple[datetime, float, float, str, float]:
        """
        Returns: (suggested_departure, expected_delay_if_now, expected_delay_if_later, reason, confidence)
        """
        now = datetime.now()
        if desired_departure is None or desired_departure < now:
            desired_departure = now + timedelta(minutes=5)

        # Look at forecast window: next 30 minutes
        window = [desired_departure + timedelta(minutes=i) for i in range(0, 30, 5)]
        # Find min congestion in window
        best_time = desired_departure
        best_congestion = current_congestion
        for ts in window:
            if ts in forecast:
                if forecast[ts] < best_congestion:
                    best_congestion = forecast[ts]
                    best_time = ts

        # Compute expected delays based on congestion
        delay_now = current_congestion * 0.05  # rough: 5 sec per congestion point
        delay_later = best_congestion * 0.05
        # But we cap to max_delay
        delay_now = min(delay_now, max_delay)
        delay_later = min(delay_later, max_delay)

        if delay_later < delay_now:
            reason = f"Better to wait until {best_time.strftime('%H:%M')}, congestion drops from {current_congestion:.0f} to {best_congestion:.0f}"
            confidence = 0.8
        else:
            best_time = desired_departure
            reason = "No significant improvement in near future; depart as planned"
            confidence = 0.6

        return best_time, round(delay_now, 1), round(delay_later, 1), reason, round(confidence, 2)