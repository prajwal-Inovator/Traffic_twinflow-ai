# ai/ripple/propagation_model.py
import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PropagationModel:
    """
    Models congestion propagation through the road network.
    Uses a graph where nodes = junctions, edges = road segments.
    """

    def __init__(self, graph: nx.Graph = None):
        self.graph = graph or nx.Graph()
        # Node attributes: capacity (vehicles/hour), current_load (vehicles/hour)
        # Edge attributes: travel_time (minutes), length (meters), capacity

    def build_from_network(self, junctions: List[Dict], roads: List[Dict]):
        """
        Build the graph from digital twin data.
        junctions: list of {id, lat, lng}
        roads: list of {start_junction_id, end_junction_id, length, speed_limit, lanes}
        """
        self.graph.clear()
        # Add nodes
        for j in junctions:
            self.graph.add_node(
                j["id"],
                lat=j.get("lat", 0),
                lng=j.get("lng", 0),
                capacity=1200,  # vehicles/hour (default)
                current_load=0,
            )
        # Add edges
        for r in roads:
            travel_time = r.get("length", 1000) / (r.get("speed_limit", 50) / 60)  # minutes
            self.graph.add_edge(
                r["start_junction_id"],
                r["end_junction_id"],
                travel_time=travel_time,
                length=r.get("length", 1000),
                capacity=1800 * r.get("lanes", 2),  # vehicles/hour
                speed_limit=r.get("speed_limit", 50),
            )
        logger.info(f"PropagationModel built with {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")

    def compute_shortest_paths(self, source: str) -> Dict[str, float]:
        """Compute shortest travel times from source to all nodes."""
        try:
            # Use Dijkstra with travel_time as weight
            lengths = nx.single_source_dijkstra_path_length(self.graph, source, weight="travel_time")
            return lengths
        except nx.NetworkXError:
            logger.warning(f"Source node {source} not in graph.")
            return {}

    def simulate_propagation(
        self,
        source_junction: str,
        initial_congestion: float = 80.0,  # percentage
        horizons: List[int] = [5, 10, 20, 30],  # minutes
    ) -> Dict[int, Dict]:
        """
        Simulate congestion propagation from a source junction.
        Returns: {horizon: {junction_id: congestion_level, affected_count, max_strength}}
        """
        if self.graph.number_of_nodes() == 0:
            logger.warning("Graph is empty; cannot simulate propagation.")
            return {}

        # Get travel times from source
        travel_times = self.compute_shortest_paths(source_junction)
        if not travel_times:
            return {}

        results = {}
        # For each horizon, compute affected junctions and their congestion levels
        for horizon in horizons:
            affected = {}
            max_strength = 0.0
            for jid, travel_time in travel_times.items():
                if travel_time <= horizon and jid != source_junction:
                    # Congestion decays with distance/travel time
                    decay = max(0, 1 - (travel_time / horizon) ** 0.8)
                    congestion = initial_congestion * decay
                    # Also consider edge capacity and current load? Keep simple for now.
                    affected[jid] = round(congestion, 1)
                    if decay > max_strength:
                        max_strength = decay
            results[horizon] = {
                "affected_junctions": affected,
                "affected_count": len(affected),
                "max_strength": round(max_strength, 3),
                "source_congestion": initial_congestion,
            }

        return results

    def get_neighbors(self, junction_id: str, radius: int = 1) -> List[str]:
        """Get neighboring junctions within a given number of hops."""
        if junction_id not in self.graph:
            return []
        return list(nx.single_source_shortest_path_length(self.graph, junction_id, cutoff=radius).keys())