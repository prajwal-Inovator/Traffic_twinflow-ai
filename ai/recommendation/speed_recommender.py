# ai/recommendation/speed_recommender.py
import numpy as np
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SpeedRecommender:
    """
    Recommends optimal speed for a given route or junction to minimize delay and fuel consumption.
    Uses a simple cost model based on traffic conditions and road geometry.
    """

    def __init__(self, speed_limit: float = 60, road_length: float = 1000):
        """
        Args:
            speed_limit: Maximum speed limit (km/h) on the road.
            road_length: Length of the road segment (meters) for delay calculation.
        """
        self.speed_limit = speed_limit
        self.road_length = road_length  # meters
        self.fuel_factor = 0.08  # liters per km at optimal speed

    def recommend(
        self,
        junction_id: str,
        current_data: Dict[str, Any],
        prediction_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Recommend optimal speed for a junction/road segment.
        current_data: vehicle_count, queue_length, avg_speed, congestion_level (0-100), etc.
        Returns: {
            'optimal_speed': float (km/h),
            'current_speed': float (km/h),
            'expected_delay': float (seconds),
            'fuel_saved': float (liters),
            'co2_saved': float (kg),
            'confidence': float,
            'reason': str,
            'timestamp': str
        }
        """
        # Extract features
        congestion = current_data.get('congestion_level', 0)
        avg_speed = current_data.get('avg_speed', 30)
        vehicle_count = current_data.get('vehicle_count', 10)
        queue_length = current_data.get('queue_length', 5)

        # Optimal speed decreases with congestion
        if congestion < 30:
            optimal_speed = min(self.speed_limit, 50 + (30 - congestion) * 0.5)
        elif congestion < 70:
            optimal_speed = 35 + (70 - congestion) * 0.3
        else:
            optimal_speed = 20 + (100 - congestion) * 0.2

        # Clamp to reasonable bounds
        optimal_speed = max(10, min(self.speed_limit, optimal_speed))

        # Calculate delay if following recommended vs current
        # Time at optimal speed (seconds) = distance / (speed * 1000/3600)
        time_optimal = self.road_length / (optimal_speed * 1000 / 3600)
        time_current = self.road_length / (avg_speed * 1000 / 3600) if avg_speed > 0 else float('inf')
        expected_delay = max(0, time_current - time_optimal)

        # Fuel and CO2 savings
        fuel_current = self._compute_fuel(avg_speed, vehicle_count)
        fuel_optimal = self._compute_fuel(optimal_speed, vehicle_count)
        fuel_saved = max(0, fuel_current - fuel_optimal)
        co2_saved = fuel_saved * 2.31  # kg CO2 per liter

        # Confidence: higher if congestion data is reliable and vehicle count not extreme
        confidence = 0.7 + 0.3 * (1 - (congestion / 100))

        return {
            "optimal_speed": round(optimal_speed, 1),
            "current_speed": round(avg_speed, 1),
            "expected_delay": round(expected_delay, 1),
            "fuel_saved": round(fuel_saved, 3),
            "co2_saved": round(co2_saved, 3),
            "confidence": round(confidence, 2),
            "reason": f"Optimal speed for {congestion:.0f}% congestion level",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def _compute_fuel(self, speed: float, vehicle_count: int) -> float:
        """
        Compute fuel consumption for a given speed and number of vehicles.
        Simple model: fuel = base_factor * distance * (1 + congestion_penalty)
        Assuming distance = road_length/1000 (km)
        """
        distance_km = self.road_length / 1000
        # Fuel efficiency peaks around 50-60 km/h
        efficiency_factor = 1.0 + 0.5 * np.exp(-((speed - 55) ** 2) / 400)
        # More vehicles means more fuel (density)
        vehicle_factor = 1.0 + 0.01 * vehicle_count
        fuel = self.fuel_factor * distance_km * efficiency_factor * vehicle_factor
        return fuel