# ai/recommendation/savings_calculator.py
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SavingsCalculator:
    """
    Calculates fuel and CO2 savings based on speed, distance, and vehicle type.
    Uses emission factors and efficiency curves.
    """

    def __init__(self):
        # Base factors: liters per km at optimal speed (50 km/h)
        self.fuel_factors = {
            "car": 0.08,
            "bus": 0.30,
            "truck": 0.35,
            "motorcycle": 0.04,
            "emergency": 0.12,
        }
        # CO2 per liter of fuel (kg CO2 / L)
        self.co2_factor = 2.31

    def calculate(
        self,
        vehicle_type: str = "car",
        distance_km: float = 5.0,
        recommended_speed: float = 50.0,
        baseline_speed: float = 30.0,  # current speed if no recommendation
    ) -> Dict[str, Any]:
        """
        Calculate fuel and CO2 savings.
        Returns: {
            'fuel_saved_liters': float,
            'co2_saved_kg': float,
            'efficiency_gain': float,  # percentage
            'details': dict
        }
        """
        base_factor = self.fuel_factors.get(vehicle_type, 0.08)

        # Efficiency curve: fuel consumption vs speed (simplified)
        # Optimal at ~50 km/h, higher at low speed due to idling, higher at high speed due to air resistance
        def efficiency_factor(speed):
            if speed < 10:
                return 1.5  # high consumption due to stop-and-go
            elif speed < 30:
                return 1.2
            elif speed < 50:
                return 0.9  # efficient range
            elif speed < 70:
                return 1.0
            else:
                return 1.1

        eff_baseline = efficiency_factor(baseline_speed)
        eff_recommended = efficiency_factor(recommended_speed)

        # Fuel consumption
        fuel_baseline = base_factor * eff_baseline * distance_km
        fuel_recommended = base_factor * eff_recommended * distance_km

        fuel_saved = fuel_baseline - fuel_recommended
        co2_saved = fuel_saved * self.co2_factor

        efficiency_gain = ((1 - (fuel_recommended / fuel_baseline)) * 100) if fuel_baseline > 0 else 0

        return {
            "fuel_saved_liters": round(fuel_saved, 3),
            "co2_saved_kg": round(co2_saved, 3),
            "efficiency_gain": round(efficiency_gain, 1),
            "details": {
                "baseline_fuel": round(fuel_baseline, 3),
                "recommended_fuel": round(fuel_recommended, 3),
                "baseline_speed": baseline_speed,
                "recommended_speed": recommended_speed,
                "distance_km": distance_km,
                "vehicle_type": vehicle_type,
            },
        }