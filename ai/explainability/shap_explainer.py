# ai/explainability/shap_explainer.py
import shap
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

class SHAPExplainer:
    """
    Wrapper for SHAP (SHapley Additive exPlanations) to explain predictions.
    Supports both TreeExplainer (for XGBoost) and KernelExplainer (generic).
    """

    def __init__(self, model, model_type: str = "tree", background_data: Optional[pd.DataFrame] = None):
        """
        Args:
            model: The trained model (e.g., XGBoost, RandomForest, or a callable).
            model_type: "tree" for tree-based models, "kernel" for others.
            background_data: Background dataset for KernelExplainer (required for kernel).
        """
        self.model = model
        self.model_type = model_type
        self.background_data = background_data
        self.explainer = None
        self._init_explainer()

    def _init_explainer(self):
        if self.model_type == "tree":
            self.explainer = shap.TreeExplainer(self.model)
        elif self.model_type == "kernel":
            if self.background_data is None:
                raise ValueError("background_data required for KernelExplainer")
            self.explainer = shap.KernelExplainer(self.model.predict, self.background_data)
        else:
            raise ValueError(f"Unsupported model_type: {self.model_type}")

    def explain_prediction(self, input_data: Union[pd.DataFrame, np.ndarray, dict]) -> Dict[str, Any]:
        """
        Explain a single prediction.
        Returns:
            {
                'base_value': float,
                'shap_values': array,
                'feature_names': list,
                'feature_importances': dict (feature -> contribution)
            }
        """
        if isinstance(input_data, dict):
            input_data = pd.DataFrame([input_data])
        elif isinstance(input_data, np.ndarray):
            input_data = pd.DataFrame(input_data)

        shap_values = self.explainer.shap_values(input_data)
        # For tree models, shap_values is a list if multi-output; we take first output.
        if isinstance(shap_values, list):
            shap_values = shap_values[0]

        base_value = self.explainer.expected_value
        if isinstance(base_value, list):
            base_value = base_value[0]

        # Combine into dict
        feature_names = input_data.columns.tolist()
        contributions = dict(zip(feature_names, shap_values[0]))

        return {
            "base_value": float(base_value),
            "shap_values": shap_values[0].tolist(),
            "feature_names": feature_names,
            "feature_importances": contributions,
        }

    def explain_global(self, X: pd.DataFrame) -> pd.DataFrame:
        """Compute global SHAP feature importance."""
        shap_values = self.explainer.shap_values(X)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        mean_abs = np.mean(np.abs(shap_values), axis=0)
        importance_df = pd.DataFrame({
            'feature': X.columns,
            'importance': mean_abs,
        }).sort_values('importance', ascending=False)
        return importance_df
        