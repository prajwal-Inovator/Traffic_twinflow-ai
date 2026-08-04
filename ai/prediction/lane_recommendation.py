# ai/prediction/lane_recommendation.py
import numpy as np
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class LaneRecommender:
    """
    Recommend optimal lane based on traffic conditions.
    Uses a rule-based approach with optional ML fallback.
    """

    def __init__(self):
        # Could load a model if needed
        self.model = None

    def recommend(
        self,
        junction_id: str,
        current_data: Dict[str, Any],
        lanes: List[int] = None
    ) -> Dict[str, Any]:
        """
        Recommend optimal lane for a given junction.
        current_data: includes vehicle_count, queue_length, occupancy per lane if available.
        Returns: {'lane': int, 'confidence': float, 'reason': str}
        """
        # In a real system, we would have per-lane data.
        # For now, we use a heuristic based on queue length and occupancy.
        queue = current_data.get('queue_length', 0)
        occupancy = current_data.get('occupancy', 0.5)
        vehicle_count = current_data.get('vehicle_count', 20)

        # Simple heuristic: if occupancy is high, recommend lane with less queue.
        # Here we simulate lanes 0,1,2 with different loads.
        if lanes is None:
            lanes = [0, 1, 2]

        # Simulate per-lane occupancy
        lane_loads = {}
        for lane in lanes:
            # Assume lane 0 is leftmost, 2 rightmost; right lane often has more turning traffic
            base = occupancy * (1 + 0.1 * (lane - 1))  # slight variation
            # Add noise
            load = min(1.0, base + np.random.normal(0, 0.05))
            lane_loads[lane] = load

        # Choose lane with lowest load
        best_lane = min(lane_loads, key=lane_loads.get)
        confidence = 1.0 - lane_loads[best_lane]

        return {
            "optimal_lane": best_lane,
            "confidence": round(confidence, 2),
            "reason": f"Lowest occupancy ({lane_loads[best_lane]:.2f}) among lanes",
            "lane_loads": lane_loads,
        }

    def update_model(self, data: List[Dict[str, Any]]):
        """Placeholder for online learning from lane choice feedback."""
        logger.info("LaneRecommender: update_model called (placeholder)")