# ai/utils/metrics.py
import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from typing import Dict, Any, Union, List
import logging

logger = logging.getLogger(__name__)

def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Compute standard regression metrics."""
    return {
        "mae": mean_absolute_error(y_true, y_pred),
        "mse": mean_squared_error(y_true, y_pred),
        "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
        "r2": r2_score(y_true, y_pred),
    }

def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, average: str = "weighted") -> Dict[str, float]:
    """Compute standard classification metrics."""
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average=average),
        "recall": recall_score(y_true, y_pred, average=average),
        "f1": f1_score(y_true, y_pred, average=average),
    }

def forecast_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Additional metrics for time-series forecasting."""
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    return {
        "mae": mae,
        "mse": mse,
        "rmse": rmse,
        "mape": mape,
    }

def log_metrics(metrics: Dict[str, float], prefix: str = ""):
    """Log metrics in a readable format."""
    if prefix:
        logger.info(f"Metrics - {prefix}:")
    for key, value in metrics.items():
        logger.info(f"  {key}: {value:.4f}")