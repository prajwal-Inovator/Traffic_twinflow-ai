# ai/prediction/carbon_predictor.py
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
import joblib
import os
import logging
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

logger = logging.getLogger(__name__)

class CarbonPredictor:
    """Predict CO₂ emissions based on traffic conditions."""

    def __init__(self, model_dir: str = "../models/carbon"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.model = None
        self.feature_columns = None
        self.emission_factor = 0.12  # kg CO2 per vehicle km (default)

    def train(self, X: pd.DataFrame, y: pd.Series, save: bool = True) -> Dict[str, float]:
        """Train a linear regression model for CO2 emissions."""
        self.model = LinearRegression()
        self.model.fit(X, y)
        self.feature_columns = X.columns.tolist()
        # Evaluate
        y_pred = self.model.predict(X)
        mae = mean_absolute_error(y, y_pred)
        logger.info(f"Carbon Predictor trained: MAE={mae:.2f}")
        if save:
            self.save()
        return {"mae": mae}

    def predict(self, features: Dict[str, Any]) -> float:
        """
        Predict CO2 emissions (kg) for a junction.
        Features: vehicle_count, avg_speed, trip_length, etc.
        """
        if self.model is not None and self.feature_columns is not None:
            df = pd.DataFrame([features])
            for col in self.feature_columns:
                if col not in df.columns:
                    df[col] = 0
            X = df[self.feature_columns]
            return self.model.predict(X)[0]
        else:
            # Fallback: use emission factor
            vehicle_count = features.get('vehicle_count', 20)
            avg_speed = features.get('avg_speed', 30)
            trip_length = features.get('trip_length', 5)  # km
            # More vehicles, lower speed -> higher emissions
            emission_factor = self.emission_factor * (1 + (40 - avg_speed) / 100)
            return vehicle_count * emission_factor * trip_length

    def save(self):
        if self.model:
            joblib.dump(self.model, os.path.join(self.model_dir, "carbon_model.pkl"))
            joblib.dump(self.feature_columns, os.path.join(self.model_dir, "feature_columns.pkl"))

    def load(self) -> bool:
        model_path = os.path.join(self.model_dir, "carbon_model.pkl")
        cols_path = os.path.join(self.model_dir, "feature_columns.pkl")
        if os.path.exists(model_path) and os.path.exists(cols_path):
            self.model = joblib.load(model_path)
            self.feature_columns = joblib.load(cols_path)
            logger.info("Carbon Predictor loaded.")
            return True
        logger.warning("Carbon Predictor model files not found. Using fallback.")
        return False