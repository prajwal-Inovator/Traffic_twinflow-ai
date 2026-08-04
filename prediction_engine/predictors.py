# prediction_engine/predictors.py
# Wrapper for AI prediction modules.
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.prediction.traffic_predictor import TrafficPredictor
from ai.prediction.speed_predictor import SpeedPredictor
from ai.prediction.carbon_predictor import CarbonPredictor
from ai.prediction.fuel_predictor import FuelPredictor

# Re-export for convenience
__all__ = [
    "TrafficPredictor",
    "SpeedPredictor",
    "CarbonPredictor",
    "FuelPredictor",
]