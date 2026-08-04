# prediction_engine/ensemble.py
import numpy as np
from typing import Dict, Any, List
import logging
from .predictors import TrafficPredictor, SpeedPredictor, CarbonPredictor, FuelPredictor

logger = logging.getLogger(__name__)

class EnsemblePredictor:
    """Ensemble of all predictors for unified prediction."""

    def __init__(self, model_dir: str = "../models"):
        self.traffic = TrafficPredictor(model_dir)
        self.speed = SpeedPredictor(model_dir)
        self.carbon = CarbonPredictor(model_dir)
        self.fuel = FuelPredictor()

    def load_models(self) -> bool:
        return all([
            self.traffic.load_models(),
            self.speed.load(),
            self.carbon.load(),
        ])

    def predict_all(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict all metrics from a single feature dict."""
        congestion = self.traffic.predict_congestion(
            junction_id=features.get("junction_id", "unknown"),
            current_data=features,
        )
        speed = self.speed.predict(features)
        carbon = self.carbon.predict(features)
        fuel = self.fuel.predict(
            vehicle_type=features.get("vehicle_type", "car"),
            distance_km=features.get("distance_km", 5.0),
            avg_speed=features.get("avg_speed", 30),
            congestion_level=congestion.get("congestion_level", 0),
        )
        return {
            "congestion": congestion,
            "speed": {"avg_speed": speed, "unit": "km/h"},
            "carbon": carbon,
            "fuel": fuel,
        }