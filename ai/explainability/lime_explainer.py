# ai/explainability/lime_explainer.py
import lime
import lime.lime_tabular
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class LIMEExplainer:
    """
    Wrapper for LIME (Local Interpretable Model-agnostic Explanations).
    Provides local explanations for individual predictions.
    """

    def __init__(
        self,
        model,
        training_data: pd.DataFrame,
        feature_names: Optional[List[str]] = None,
        mode: str = "regression",  # or "classification"
        discretize_continuous: bool = True,
    ):
        """
        Args:
            model: A callable that takes a 2D numpy array and returns predictions.
            training_data: Background data for the explainer.
            feature_names: List of feature names.
            mode: "regression" or "classification".
            discretize_continuous: Whether to discretize continuous features.
        """
        self.model = model
        self.training_data = training_data.values if isinstance(training_data, pd.DataFrame) else training_data
        self.feature_names = feature_names or [f"feature_{i}" for i in range(self.training_data.shape[1])]
        self.mode = mode
        self.discretize_continuous = discretize_continuous
        self.explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=self.training_data,
            feature_names=self.feature_names,
            mode=mode,
            discretize_continuous=discretize_continuous,
            verbose=False,
        )

    def explain_prediction(self, input_data: Union[pd.DataFrame, np.ndarray, dict]) -> Dict[str, Any]:
        """
        Explain a single prediction.
        Returns:
            {
                'explanation': dict with feature contributions,
                'local_prediction': float,
                'intercept': float,
                'feature_values': dict
            }
        """
        if isinstance(input_data, dict):
            input_data = pd.DataFrame([input_data])
        if isinstance(input_data, pd.DataFrame):
            input_data = input_data.values[0]

        # Ensure input is a 2D array of shape (1, n_features)
        if len(input_data.shape) == 1:
            input_data = input_data.reshape(1, -1)

        # Get explanation
        exp = self.explainer.explain_instance(
            input_data[0],
            self.model.predict,
            num_features=len(self.feature_names),
        )

        # Extract feature contributions
        contributions = {}
        for feat, weight in exp.as_list():
            contributions[feat] = weight

        return {
            "explanation": contributions,
            "local_prediction": float(exp.local_pred[0]) if self.mode == "regression" else None,
            "intercept": float(exp.intercept[0]) if hasattr(exp, 'intercept') else None,
            "feature_values": dict(zip(self.feature_names, input_data[0].tolist())),
        }

    def show_explanation(self, input_data: Union[pd.DataFrame, np.ndarray, dict], show_in_notebook: bool = False):
        """Generate an HTML explanation for display."""
        if isinstance(input_data, dict):
            input_data = pd.DataFrame([input_data])
        if isinstance(input_data, pd.DataFrame):
            input_data = input_data.values[0]
        if len(input_data.shape) == 1:
            input_data = input_data.reshape(1, -1)

        exp = self.explainer.explain_instance(
            input_data[0],
            self.model.predict,
            num_features=len(self.feature_names),
        )
        if show_in_notebook:
            exp.show_in_notebook()
        return exp.as_html()