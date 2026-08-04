# digital_twin/twin_engine.py
import logging
from typing import Optional, Dict, Any, List, Tuple
import networkx as nx
import geopandas as gpd
from .osm_importer import OSMImporter
from .network_builder import NetworkBuilder
from .geospatial.geo_utils import haversine_distance

logger = logging.getLogger(__name__)

class TwinEngine:
    """Orchestrator for the digital twin: loads network, provides query methods, syncs with live data."""

    def __init__(self, config_path: str = "digital_twin/config.yaml"):
        self.importer = OSMImporter(config_path)
        self.builder = NetworkBuilder(self.importer)
        self.graph = self.builder.build_network()
        self.gdf_nodes = self.importer.get_nodes_gdf()
        self.gdf_edges = self.importer.get_edges_gdf()
        self._junction_id_to_osm_node: Dict[str, int] = {}  # mapping from our junction IDs to OSM node IDs

    def get_network_graph(self) -> nx.MultiDiGraph:
        return self.graph

    def get_node_geometry(self, node_id: int) -> Tuple[float, float]:
        """Return (lat, lon) for an OSM node."""
        node_row = self.gdf_nodes.loc[node_id]
        return node_row.geometry.y, node_row.geometry.x

    def get_edge_geometry(self, u: int, v: int, key: int = 0) -> Optional[LineString]:
        """Return LineString geometry of an edge."""
        if self.graph.has_edge(u, v, key):
            return self.graph[u][v][key].get('geometry')
        return None

    def compute_shortest_path(self, origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float) -> List[int]:
        """Return list of OSM node IDs along shortest path."""
        orig_node = self.builder.get_nearest_node(origin_lat, origin_lon)
        dest_node = self.builder.get_nearest_node(dest_lat, dest_lon)
        try:
            path = nx.shortest_path(self.graph, orig_node, dest_node, weight='travel_time')
            return path
        except nx.NetworkXNoPath:
            logger.warning(f"No path found from node {orig_node} to {dest_node}")
            return []

    def get_junction_id_for_node(self, node_id: int) -> Optional[str]:
        """Map OSM node to our internal junction ID (if any)."""
        # In a real system, we would have a mapping table; for now, we can use the node_id as junction id.
        return str(node_id)

    def get_node_for_junction_id(self, junction_id: str) -> Optional[int]:
        """Map internal junction ID to OSM node."""
        # For simplicity, we assume junction_id is the node_id string.
        try:
            return int(junction_id)
        except ValueError:
            return None

    def get_nearest_junction(self, lat: float, lon: float) -> Optional[str]:
        """Find nearest junction (OSM node) to given coordinates."""
        node = self.builder.get_nearest_node(lat, lon)
        return self.get_junction_id_for_node(node)

    def update_live_traffic(self, junction_id: str, vehicle_count: int, queue_length: int, signal_phase: str):
        """Update the graph with live traffic data (for simulation/recommendation)."""
        node = self.get_node_for_junction_id(junction_id)
        if node is not None:
            # Store in graph node attributes or a separate data structure
            if node in self.graph.nodes:
                self.graph.nodes[node]['vehicle_count'] = vehicle_count
                self.graph.nodes[node]['queue_length'] = queue_length
                self.graph.nodes[node]['signal_phase'] = signal_phase
                logger.debug(f"Updated junction {junction_id} with traffic data")
            else:
                logger.warning(f"Node {node} not in graph")

    def get_congestion_map(self) -> Dict[str, float]:
        """Return a dict of junction_id -> congestion level (0-100) for all nodes."""
        congestion = {}
        for node, data in self.graph.nodes(data=True):
            # Placeholder: if we have vehicle_count and capacity, compute congestion
            # For now, use a dummy value
            vehicle_count = data.get('vehicle_count', 0)
            capacity = data.get('capacity', 100)  # dummy
            if capacity > 0:
                congestion_level = min(100, (vehicle_count / capacity) * 100)
            else:
                congestion_level = 0
            congestion[str(node)] = congestion_level
        return congestion

    def get_ripple_effect(self, junction_id: str, time_horizon: int) -> Dict[str, Any]:
        """Simulate ripple effect over given time horizon (minutes)."""
        # Placeholder: in later steps, we'll use SUMO or a propagation model.
        # For now, return dummy data.
        node = self.get_node_for_junction_id(junction_id)
        affected = [str(n) for n in self.graph.neighbors(node)] if node else []
        return {
            "junction_id": junction_id,
            "time_horizon": time_horizon,
            "predicted_congestion": 75.0,
            "affected_junctions": affected[:10],
            "propagation_strength": 0.6,
        }