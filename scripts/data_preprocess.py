# scripts/data_preprocess.py
import pandas as pd
import numpy as np
import os
import sys
import logging
from datetime import datetime

def preprocess_traffic_data(input_file: str, output_file: str):
    """Clean and format traffic CSV data."""
    df = pd.read_csv(input_file)
    # Handle missing values
    df = df.dropna()
    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Add derived features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    # Save
    df.to_csv(output_file, index=False)
    print(f"Preprocessed data saved to {output_file}")

if __name__ == "__main__":
    preprocess_traffic_data("../datasets/raw/01_road_network.csv", "../datasets/processed/01_road_network_clean.csv")