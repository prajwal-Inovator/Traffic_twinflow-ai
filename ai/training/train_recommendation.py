# ai/training/train_recommendation.py
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recommendation.recommendation_engine import RecommendationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_recommendation():
    engine = RecommendationEngine()
    sample_data = {
        "vehicle_count": 25,
        "queue_length": 8,
        "avg_speed": 25,
        "congestion_level": 65,
    }
    pred = {"congestion_level": 70}
    signal = {"green_time": 25, "red_time": 35, "cycle_time": 60}
    rec = engine.get_full_recommendation("j1", sample_data, pred, signal)
    logger.info(f"Recommendation: {rec}")

if __name__ == "__main__":
    test_recommendation()