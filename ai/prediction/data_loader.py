# ai/prediction/data_loader.py
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PredictionDataLoader:
    """Load and preprocess data for prediction models."""

    def __init__(self, dataset_path: str = "../datasets/processed"):
        self.dataset_path = dataset_path

    def load_traffic_data(self, junction_id: str, days: int = 30) -> pd.DataFrame:
        """Load historical traffic data for a junction."""
        # In production, we would load from MongoDB
        # For now, we'll simulate or load from CSV files
        # Example: load aggregated data
        file_path = os.path.join(self.dataset_path, f"junction_{junction_id}.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        else:
            logger.warning(f"No data file found for junction {junction_id}. Generating synthetic data.")
            return self._generate_synthetic_data(junction_id, days)

    def _generate_synthetic_data(self, junction_id: str, days: int) -> pd.DataFrame:
        """Generate synthetic traffic data for demo/development."""
        start_date = datetime.now() - timedelta(days=days)
        timestamps = [start_date + timedelta(minutes=5*i) for i in range(days*24*12)]
        data = {
            'timestamp': timestamps,
            'vehicle_count': np.random.poisson(20, len(timestamps)),
            'queue_length': np.random.exponential(5, len(timestamps)),
            'avg_speed': np.random.normal(30, 10, len(timestamps)),
            'occupancy': np.random.uniform(0.1, 0.8, len(timestamps)),
            'hour': [t.hour for t in timestamps],
            'day_of_week': [t.weekday() for t in timestamps],
            'is_weekend': [1 if t.weekday() >= 5 else 0 for t in timestamps],
        }
        df = pd.DataFrame(data)
        df['junction_id'] = junction_id
        return df

    def create_sequence_features(
        self,
        df: pd.DataFrame,
        target_col: str,
        lookback: int = 12,  # 12 * 5min = 60 min
        forecast_horizon: int = 6  # 6 * 5min = 30 min
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create features for time-series prediction (LSTM).
        Returns (X, y) where X is sequence of lookback steps, y is forecast_horizon steps ahead.
        """
        data = df[target_col].values
        X, y = [], []
        for i in range(lookback, len(data) - forecast_horizon):
            X.append(data[i-lookback:i])
            y.append(data[i:i+forecast_horizon])
        return np.array(X), np.array(y)

    def get_tabular_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract tabular features for XGBoost."""
        features = df[['hour', 'day_of_week', 'is_weekend', 'vehicle_count', 'queue_length', 'occupancy']].copy()
        # Add lag features
        for lag in [1, 3, 6, 12]:  # 5min, 15min, 30min, 60min
            features[f'vehicle_lag_{lag}'] = df['vehicle_count'].shift(lag)
        features = features.dropna()
        return features