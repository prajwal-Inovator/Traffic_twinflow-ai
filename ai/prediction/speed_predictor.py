# ai/prediction/speed_predictor.py
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
import joblib
import os
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logger = logging.getLogger(__name__)

class SpeedPredictor:
    """Predict average speed on a road segment or junction."""

    def __init__(self, model_dir: str = "../models/speed"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.model = None
        self.feature_columns = None

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        save: bool = True
    ) -> Dict[str, float]:
        """
        Train a Random Forest regressor for speed prediction.
        Features: hour, day_of_week, vehicle_count, queue_length, occupancy, etc.
        Target: average speed (km/h)
        """
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        # Model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1,
        )
        self.model.fit(X_train, y_train)
        self.feature_columns = X.columns.tolist()
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        logger.info(f"Speed Predictor trained: MAE={mae:.2f}, MSE={mse:.2f}, R2={r2:.2f}")
        if save:
            self.save()
        return {"mae": mae, "mse": mse, "r2": r2}

    def predict(self, features: Dict[str, Any]) -> float:
        """Predict speed from feature dict."""
        if self.model is None:
            self.load()
        df = pd.DataFrame([features])
        # Ensure all columns are present
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0
        X = df[self.feature_columns]
        pred = self.model.predict(X)[0]
        return max(0, min(120, pred))  # clamp to reasonable speed range

    def save(self):
        if self.model:
            joblib.dump(self.model, os.path.join(self.model_dir, "speed_model.pkl"))
            joblib.dump(self.feature_columns, os.path.join(self.model_dir, "feature_columns.pkl"))

    def load(self) -> bool:
        model_path = os.path.join(self.model_dir, "speed_model.pkl")
        cols_path = os.path.join(self.model_dir, "feature_columns.pkl")
        if os.path.exists(model_path) and os.path.exists(cols_path):
            self.model = joblib.load(model_path)
            self.feature_columns = joblib.load(cols_path)
            logger.info("Speed Predictor loaded.")
            return True
        logger.warning("Speed Predictor model files not found. Using fallback.")
        return False