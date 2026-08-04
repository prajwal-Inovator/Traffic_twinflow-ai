# ai/prediction/fuel_predictor.py
import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FuelPredictor:
    """Predict fuel consumption based on traffic conditions and vehicle type."""

    def __init__(self):
        # Fuel consumption factors (liters per km) by vehicle type
        self.fuel_factors = {
            "car": 0.08,
            "bus": 0.30,
            "truck": 0.35,
            "motorcycle": 0.04,
            "emergency": 0.12,
        }

    def predict(
        self,
        vehicle_type: str = "car",
        distance_km: float = 5.0,
        avg_speed: float = 30.0,
        congestion_level: float = 0.0
    ) -> Dict[str, Any]:
        """
        Predict fuel consumption for a vehicle or aggregated fleet.
        Returns: fuel_consumption_liters, co2_emissions_kg, efficiency_metrics
        """
        base_factor = self.fuel_factors.get(vehicle_type, 0.08)
        # Speed affects efficiency: optimal around 50-60 km/h, less at low speed
        speed_efficiency = 1.0 + 0.5 * np.exp(-((avg_speed - 55) ** 2) / 400)
        # Congestion increases fuel consumption
        congestion_factor = 1.0 + congestion_level * 0.01  # 1% per congestion point
        effective_factor = base_factor * speed_efficiency * congestion_factor
        fuel = effective_factor * distance_km
        co2 = fuel * 2.31  # kg CO2 per liter of petrol (approx)

        return {
            "fuel_consumption_liters": round(fuel, 3),
            "co2_emissions_kg": round(co2, 3),
            "efficiency_km_per_liter": round(distance_km / fuel if fuel > 0 else 0, 1),
            "factors": {
                "base_factor": base_factor,
                "speed_efficiency": round(speed_efficiency, 2),
                "congestion_factor": round(congestion_factor, 2),
            },
        }

    def predict_fleet(self, vehicles: list, distance_km: float = 5.0) -> Dict[str, float]:
        """Aggregate prediction for a fleet of vehicles."""
        total_fuel = 0
        total_co2 = 0
        for v in vehicles:
            v_type = v.get("type", "car")
            speed = v.get("speed", 30)
            # Compute congestion level from speed (simplified)
            congestion = max(0, 60 - speed) / 60 * 100
            pred = self.predict(v_type, distance_km, speed, congestion)
            total_fuel += pred["fuel_consumption_liters"]
            total_co2 += pred["co2_emissions_kg"]
        return {
            "total_fuel_liters": round(total_fuel, 2),
            "total_co2_kg": round(total_co2, 2),
            "vehicle_count": len(vehicles),
        }