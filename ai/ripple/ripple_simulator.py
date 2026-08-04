# ai/ripple/ripple_simulator.py
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import networkx as nx
from .propagation_model import PropagationModel

logger = logging.getLogger(__name__)

class RippleSimulator:
    """
    Simulates and stores ripple effects of signal changes.
    """

    def __init__(self, propagation_model: PropagationModel = None):
        self.model = propagation_model or PropagationModel()
        self.simulation_history: List[Dict] = []

    def load_network(self, junctions: List[Dict], roads: List[Dict]):
        """Load road network into the propagation model."""
        self.model.build_from_network(junctions, roads)

    def simulate_ripple(
        self,
        source_junction: str,
        initial_congestion: float = 80.0,
        horizons: List[int] = [5, 10, 20, 30],
    ) -> Dict[str, Any]:
        """
        Run ripple simulation for a source junction.
        Returns structured results with metadata.
        """
        if not self.model.graph:
            logger.error("Propagation model graph is empty. Call load_network first.")
            return {"error": "Network not loaded"}

        start_time = datetime.utcnow()
        results = self.model.simulate_propagation(source_junction, initial_congestion, horizons)
        end_time = datetime.utcnow()

        # Build final output
        output = {
            "source_junction": source_junction,
            "initial_congestion": initial_congestion,
            "horizons": {},
            "timestamp": start_time.isoformat() + "Z",
            "simulation_time_ms": (end_time - start_time).total_seconds() * 1000,
        }

        for horizon, data in results.items():
            output["horizons"][str(horizon)] = {
                "affected_count": data["affected_count"],
                "max_strength": data["max_strength"],
                "affected_junctions": data["affected_junctions"],
                "source_congestion": data.get("source_congestion", initial_congestion),
            }

        self.simulation_history.append(output)
        logger.info(f"Ripple simulation for {source_junction} completed.")
        return output

    async def simulate_ripple_async(
        self,
        source_junction: str,
        initial_congestion: float = 80.0,
        horizons: List[int] = [5, 10, 20, 30],
    ) -> Dict[str, Any]:
        """Asynchronous wrapper."""
        return await asyncio.to_thread(
            self.simulate_ripple, source_junction, initial_congestion, horizons
        )

    def get_historical_simulations(self, limit: int = 10) -> List[Dict]:
        """Get recent simulation results."""
        return self.simulation_history[-limit:]

    def clear_history(self):
        self.simulation_history.clear()