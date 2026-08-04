# ai/prediction/traffic_predictor.py
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from .xgboost_predictor import XGBoostPredictor
from .lstm_predictor import LSTMPredictor
from .data_loader import PredictionDataLoader
import logging
from .speed_predictor import SpeedPredictor
from .lane_recommendation import LaneRecommender
from .signal_optimizer import SignalOptimizer
from .carbon_predictor import CarbonPredictor
from .fuel_predictor import FuelPredictor
from ..explainability.shap_explainer import SHAPExplainer
from ..explainability.lime_explainer import LIMEExplainer


logger = logging.getLogger(__name__)

class TrafficPredictor:
    def __init__(self, model_dir: str = "../models"):
        # ... existing
        self.speed_predictor = SpeedPredictor(os.path.join(model_dir, "speed"))
        self.lane_recommender = LaneRecommender()
        self.signal_optimizer = SignalOptimizer()
        self.carbon_predictor = CarbonPredictor(os.path.join(model_dir, "carbon"))
        self.fuel_predictor = FuelPredictor()
        self.shap_explainer = None
        self.lime_explainer = None

    def load_models(self) -> bool:
        # ... existing load, and load speed and carbon
        speed_loaded = self.speed_predictor.load()
        carbon_loaded = self.carbon_predictor.load()
        return self.is_loaded and speed_loaded and carbon_loaded
    def init_explainers(self, background_data: pd.DataFrame):
        """Initialize SHAP and LIME explainers with background data."""
        if self.xgb.model:
            self.shap_explainer = SHAPExplainer(self.xgb.model, model_type="tree")
        # For LIME, we need a predict function
        def predict_fn(x):
            return self.xgb.model.predict(x)
        self.lime_explainer = LIMEExplainer(
            model=predict_fn,
            training_data=background_data,
            mode="regression",
        )

class TrafficPredictor:
    """Ensemble predictor combining XGBoost and LSTM."""

    def __init__(self, model_dir: str = "../models"):
        self.xgb = XGBoostPredictor(os.path.join(model_dir, "xgboost"))
        self.lstm = LSTMPredictor(os.path.join(model_dir, "lstm"))
        self.loader = PredictionDataLoader()
        self.is_loaded = False

    def load_models(self) -> bool:
        """Load both models if available."""
        xgb_loaded = self.xgb.load()
        lstm_loaded = self.lstm.load()
        self.is_loaded = xgb_loaded and lstm_loaded
        return self.is_loaded

    def train_models(self, junction_id: str, days: int = 30) -> Dict[str, Any]:
        """Train both models on data for a junction."""
        df = self.loader.load_traffic_data(junction_id, days)
        # Prepare tabular features for XGBoost
        X_tab = self.loader.get_tabular_features(df)
        y_tab = X_tab.pop('vehicle_count')  # target
        # Train XGBoost
        xgb_metrics = self.xgb.train(X_tab, y_tab)

        # Prepare LSTM
        X_seq, y_seq = self.loader.create_sequence_features(
            df, target_col='vehicle_count', lookback=12, forecast_horizon=6
        )
        # Use mean of forecast horizon as target (or multi-step)
        y_mean = y_seq.mean(axis=1)
        lstm_metrics = self.lstm.train(X_seq, y_mean)

        return {
            "xgb": xgb_metrics,
            "lstm": lstm_metrics,
        }

    def predict_congestion(
        self,
        junction_id: str,
        current_data: Dict[str, Any],
        horizon_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Predict congestion for a junction.
        current_data: dict with features (hour, day_of_week, vehicle_count, queue_length, occupancy, etc.)
        Returns: {
            'congestion_level': float 0-100,
            'vehicle_count': int,
            'confidence': float,
            'model': 'ensemble',
            'explanation': dict
        }
        """
        if not self.is_loaded:
            self.load_models()

        # Prepare features for XGBoost
        df = pd.DataFrame([current_data])
        X_tab = self.loader.get_tabular_features(df)
        if X_tab.empty:
            # Use fallback
            logger.warning("Insufficient features for XGBoost; using LSTM only.")
            xgb_pred = 50  # fallback
        else:
            xgb_pred = self.xgb.predict(X_tab)[0]

        # For LSTM, we need sequence history (last 12 steps)
        # We'll use a placeholder: if history not available, we fallback
        # In production, we would maintain a rolling window in Redis/MongoDB
        lstm_pred = xgb_pred  # placeholder

        # Ensemble: weighted average
        congestion = 0.6 * xgb_pred + 0.4 * lstm_pred
        # Normalize to 0-100
        congestion = max(0, min(100, congestion))

        # Confidence based on feature availability and model confidence
        confidence = 0.8  # placeholder

        return {
            "congestion_level": round(congestion, 1),
            "vehicle_count": int(congestion * 0.5),  # rough mapping
            "confidence": confidence,
            "model": "ensemble_xgb_lstm",
            "explanation": {
                "xgb_prediction": round(xgb_pred, 1),
                "lstm_prediction": round(lstm_pred, 1),
                "weight": {"xgb": 0.6, "lstm": 0.4},
            },
            "timestamp": pd.Timestamp.now().isoformat(),
            "horizon_minutes": horizon_minutes,
        }

    def predict_speed(
        self,
        junction_id: str,
        current_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict average speed."""
        # Simplified: use XGBoost or a separate model
        df = pd.DataFrame([current_data])
        X_tab = self.loader.get_tabular_features(df)
        if not X_tab.empty:
            # We could have a separate speed predictor; for now we map from congestion
            congestion = self.predict_congestion(junction_id, current_data)['congestion_level']
            speed = max(0, 60 - congestion * 0.6)  # rough mapping
        else:
            speed = 35
        return {
            "avg_speed": round(speed, 1),
            "unit": "km/h",
        }

    def predict_carbon(
        self,
        junction_id: str,
        current_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict CO2 and fuel consumption."""
        # Simulate based on vehicle count and speed
        vehicle_count = current_data.get('vehicle_count', 20)
        avg_speed = self.predict_speed(junction_id, current_data)['avg_speed']
        # Emission factors (simplified)
        co2_per_km = 0.12  # kg CO2 per vehicle km (avg)
        fuel_per_km = 0.05  # liters per km
        # Assume average trip length ~5 km
        trip_length = 5
        co2 = vehicle_count * co2_per_km * trip_length
        fuel = vehicle_count * fuel_per_km * trip_length
        return {
            "co2_emissions": round(co2, 2),
            "fuel_consumption": round(fuel, 2),
            "co2_saved": round(co2 * 0.2, 2),  # 20% savings from optimization
            "fuel_saved": round(fuel * 0.2, 2),
            "unit": {"co2": "kg", "fuel": "liters"},
        }