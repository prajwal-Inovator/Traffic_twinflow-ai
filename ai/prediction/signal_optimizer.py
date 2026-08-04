# ai/prediction/signal_optimizer.py
import numpy as np
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class SignalOptimizer:
    """
    Optimize traffic signal timings (green/red times) based on traffic conditions.
    Implements a simple adaptive control algorithm.
    """

    def __init__(self):
        self.min_green = 10
        self.max_green = 60
        self.min_red = 5
        self.max_red = 60

    def optimize(
        self,
        junction_id: str,
        current_data: Dict[str, Any],
        current_phase: str = "green"
    ) -> Dict[str, Any]:
        """
        Suggest optimal green/red times.
        current_data: vehicle_count, queue_length, emergency_status, bus_priority, etc.
        Returns: {'green_time': int, 'red_time': int, 'priority': float, 'reason': str}
        """
        vehicle_count = current_data.get('vehicle_count', 10)
        queue_length = current_data.get('queue_length', 5)
        emergency = current_data.get('emergency_status', False)
        bus_priority = current_data.get('bus_priority', False)

        # Base green time proportional to vehicle count (but within bounds)
        base_green = min(self.max_green, max(self.min_green, vehicle_count * 1.5))
        base_red = min(self.max_red, max(self.min_red, queue_length * 2))

        # Adjust for emergency
        if emergency:
            green_time = self.max_green
            red_time = self.min_red
            reason = "Emergency vehicle priority"
            priority = 1.0
        elif bus_priority:
            green_time = min(self.max_green, base_green * 1.3)
            red_time = max(self.min_red, base_red * 0.7)
            reason = "Bus priority"
            priority = 0.9
        else:
            green_time = base_green
            red_time = base_red
            reason = "Normal traffic conditions"
            priority = 0.6 + 0.3 * (vehicle_count / 50)  # higher priority if more vehicles

        return {
            "green_time": int(green_time),
            "red_time": int(red_time),
            "priority": round(priority, 2),
            "reason": reason,
            "confidence": 0.85,  # heuristic confidence
            "timestamp": pd.Timestamp.now().isoformat(),
        }

    def adapt(
        self,
        historical_data: List[Dict[str, Any]]
    ):
        """Adapt signal timing based on historical data (e.g., using reinforcement learning)."""
        logger.info("SignalOptimizer: adapt called (placeholder)")