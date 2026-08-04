# ai/recommendation/lane_recommender.py
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LaneRecommender:
    """
    Recommends the optimal lane for a driver based on traffic conditions.
    Uses per‑lane occupancy and queue length data (simulated or from detectors).
    """

    def __init__(self, num_lanes: int = 3):
        self.num_lanes = num_lanes
        # Historical lane usage could be used to train a model; here we use heuristics.

    def recommend(
        self,
        junction_id: str,
        current_data: Dict[str, Any],
        lane_data: Optional[Dict[int, Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Recommend optimal lane.
        current_data: vehicle_count, queue_length, congestion_level, etc.
        lane_data: optional dict with per‑lane metrics (occupancy, queue).
        Returns: {
            'optimal_lane': int,
            'confidence': float,
            'reason': str,
            'lane_loads': dict,
            'timestamp': str
        }
        """
        # If no lane data, simulate based on overall congestion
        if lane_data is None:
            lane_data = self._simulate_lane_data(current_data)

        # Choose lane with lowest load (occupancy + queue)
        best_lane = None
        best_score = float('inf')
        loads = {}
        for lane, data in lane_data.items():
            occupancy = data.get('occupancy', 0.5)
            queue = data.get('queue_length', 0)
            score = occupancy * 0.7 + (queue / 10) * 0.3
            loads[lane] = round(score, 2)
            if score < best_score:
                best_score = score
                best_lane = lane

        confidence = 0.8 if best_lane is not None else 0.5

        return {
            "optimal_lane": best_lane,
            "confidence": round(confidence, 2),
            "reason": f"Lowest congestion (score {best_score:.2f})",
            "lane_loads": loads,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def _simulate_lane_data(self, current_data: Dict) -> Dict[int, Dict]:
        """Generate synthetic lane data from overall congestion."""
        congestion = current_data.get('congestion_level', 50)
        queue = current_data.get('queue_length', 5)
        # Simulate variation across lanes (right lane often busier for turning)
        lanes = {}
        for i in range(self.num_lanes):
            # Lane 0: leftmost, often less congested; lane 2: rightmost, often more
            base_occ = congestion / 100
            if i == 0:
                occ = base_occ * (1 - 0.1)
            elif i == 1:
                occ = base_occ * (1 + 0.05)
            else:
                occ = base_occ * (1 + 0.15)
            occ = min(1, max(0, occ))
            lanes[i] = {
                'occupancy': round(occ, 2),
                'queue_length': max(0, queue + (i - 1) * 2),
            }
        return lanes