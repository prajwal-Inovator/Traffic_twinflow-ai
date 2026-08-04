# ai/training/train_traffic.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prediction.traffic_predictor import TrafficPredictor
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    predictor = TrafficPredictor(model_dir="../models")
    junction_id = "junction_1"  # or loop over all junctions
    metrics = predictor.train_models(junction_id, days=30)
    print(f"Training metrics: {metrics}")