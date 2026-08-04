# ai/prediction/xgboost_predictor.py
import xgboost as xgb
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import joblib
import os
import logging
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logger = logging.getLogger(__name__)

class XGBoostPredictor:
    """XGBoost model for tabular traffic prediction."""

    def __init__(self, model_dir: str = "../models/xgboost"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.model = None
        self.feature_columns = None

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        params: Dict[str, Any] = None,
        save: bool = True
    ) -> Dict[str, float]:
        """Train XGBoost model."""
        if params is None:
            params = {
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
            }
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        # Train
        self.model = xgb.XGBRegressor(**params)
        self.model.fit(X_train, y_train)
        self.feature_columns = X.columns.tolist()
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        logger.info(f"XGBoost trained: MAE={mae:.2f}, MSE={mse:.2f}, R2={r2:.2f}")
        # Save
        if save:
            self.save()
        return {"mae": mae, "mse": mse, "r2": r2}

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        if self.model is None:
            raise RuntimeError("Model not loaded/trained.")
        # Ensure columns match
        X = X[self.feature_columns]
        return self.model.predict(X)

    def save(self):
        """Save model and feature columns."""
        if self.model:
            joblib.dump(self.model, os.path.join(self.model_dir, "xgboost_model.pkl"))
            joblib.dump(self.feature_columns, os.path.join(self.model_dir, "feature_columns.pkl"))
            logger.info(f"XGBoost model saved to {self.model_dir}")

    def load(self):
        """Load model and feature columns."""
        model_path = os.path.join(self.model_dir, "xgboost_model.pkl")
        cols_path = os.path.join(self.model_dir, "feature_columns.pkl")
        if os.path.exists(model_path) and os.path.exists(cols_path):
            self.model = joblib.load(model_path)
            self.feature_columns = joblib.load(cols_path)
            logger.info("XGBoost model loaded.")
            return True
        logger.warning("XGBoost model files not found.")
        return False