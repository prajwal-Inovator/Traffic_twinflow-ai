# ai/utils/data_loader.py
import pandas as pd
import numpy as np
import os
import json
import csv
from typing import Union, List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    """Generic data loader for various formats."""

    @staticmethod
    def load_csv(file_path: str, **kwargs) -> pd.DataFrame:
        """Load CSV file with pandas."""
        return pd.read_csv(file_path, **kwargs)

    @staticmethod
    def load_json(file_path: str, **kwargs) -> Union[Dict, List]:
        """Load JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f, **kwargs)

    @staticmethod
    def load_parquet(file_path: str, **kwargs) -> pd.DataFrame:
        """Load Parquet file."""
        return pd.read_parquet(file_path, **kwargs)

    @staticmethod
    def load_dataset_from_directory(directory: str, pattern: str = "*.csv") -> List[pd.DataFrame]:
        """Load multiple files from a directory."""
        import glob
        files = glob.glob(os.path.join(directory, pattern))
        dfs = []
        for f in files:
            try:
                df = pd.read_csv(f)
                dfs.append(df)
            except Exception as e:
                logger.error(f"Error loading {f}: {e}")
        return dfs

    @staticmethod
    def split_data(df: pd.DataFrame, target_col: str, test_size: float = 0.2):
        """Split data into features and target, train and test."""
        from sklearn.model_selection import train_test_split
        X = df.drop(columns=[target_col])
        y = df[target_col]
        return train_test_split(X, y, test_size=test_size, random_state=42)