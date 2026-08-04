# ai/recommendation/departure_optimizer.py
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from .optimizers import GeneticOptimizer

logger = logging.getLogger(__name__)

class DepartureOptimizer:
    """
    Recommends optimal departure time to minimize travel time and fuel consumption.
    Uses a simple traffic model with time‑of‑day patterns.
    """

    def __init__(self, route_length: float = 10.0, avg_speed: float = 30):
        """
        Args:
            route_length: Length of route in km.
            avg_speed: Average speed during off‑peak (km/h).
        """
        self.route_length = route_length
        self.avg_speed = avg_speed
        self.optimizer = GeneticOptimizer(
            population_size=30,
            generations=50,
            mutation_rate=0.2,
        )

    def recommend(
        self,
        junction_id: str,
        current_data: Dict[str, Any],
        desired_arrival_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Recommend optimal departure time.
        current_data: includes hour, day_of_week, congestion_level, etc.
        desired_arrival_time: optional; if provided, compute departure time backwards.
        Returns: {
            'departure_time': str (ISO),
            'arrival_time': str (ISO),
            'expected_delay': float (minutes),
            'fuel_saved': float (liters),
            'co2_saved': float (kg),
            'confidence': float,
            'reason': str,
        }
        """
        now = datetime.utcnow()
        if desired_arrival_time is None:
            # Default: arrival at 9 AM (if before) or 1 hour from now
            target = datetime(now.year, now.month, now.day, 9, 0, 0)
            if target < now:
                target = now + timedelta(hours=1)
        else:
            target = desired_arrival_time

        # Objective function: minimize a cost that includes travel time, fuel, and arrival penalty
        def cost_function(params):
            departure_offset = params[0]  # minutes before target
            travel_speed = params[1]      # km/h (average over route)
            # Bound checks
            if departure_offset < 0 or departure_offset > 120:
                return 1e9
            if travel_speed < 5 or travel_speed > 80:
                return 1e9

            departure = target - timedelta(minutes=departure_offset)
            # If departure is in the past, penalize heavily
            if departure < now:
                return 1e9

            # Travel time in hours = distance / speed
            travel_hours = self.route_length / travel_speed
            arrival = departure + timedelta(hours=travel_hours)

            # Penalty for arriving too early or late
            arrival_penalty = abs((arrival - target).total_seconds()) / 60  # minutes

            # Fuel consumption: higher at lower speeds
            fuel = self.route_length * (0.08 + 0.02 * (self.avg_speed / travel_speed))

            # Combine: travel time + arrival penalty + fuel penalty
            cost = travel_hours * 60 + arrival_penalty * 2 + fuel * 50
            return cost

        # Bounds: departure offset (0-120 min), speed (10-60 km/h)
        bounds = [(0, 120), (10, 60)]
        result = self.optimizer.optimize(
            objective=cost_function,
            bounds=bounds,
            maximize=False,
        )

        if result['best_individual'] is None:
            # Fallback
            depart_offset = 30
            travel_speed = self.avg_speed
        else:
            depart_offset, travel_speed = result['best_individual']

        departure = target - timedelta(minutes=depart_offset)
        travel_time_hours = self.route_length / travel_speed
        arrival = departure + timedelta(hours=travel_time_hours)

        # Expected delay = travel time at recommended speed vs optimal speed
        optimal_speed = min(60, self.avg_speed * 1.2)
        optimal_time = self.route_length / optimal_speed
        expected_delay = travel_time_hours - optimal_time

        # Fuel savings vs baseline
        fuel_baseline = self.route_length * 0.08
        fuel_recommended = self.route_length * (0.08 + 0.02 * (self.avg_speed / travel_speed))
        fuel_saved = max(0, fuel_baseline - fuel_recommended)
        co2_saved = fuel_saved * 2.31

        confidence = 0.7  # genetic algorithm has some uncertainty

        return {
            "departure_time": departure.isoformat() + "Z",
            "arrival_time": arrival.isoformat() + "Z",
            "expected_delay": round(expected_delay * 60, 1),  # minutes
            "fuel_saved": round(fuel_saved, 3),
            "co2_saved": round(co2_saved, 3),
            "confidence": round(confidence, 2),
            "reason": f"Depart {depart_offset:.0f} minutes before target, speed {travel_speed:.1f} km/h",
            "travel_speed": round(travel_speed, 1),
            "travel_time_minutes": round(travel_time_hours * 60, 1),
        }