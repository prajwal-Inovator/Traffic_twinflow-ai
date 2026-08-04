# digital_twin/network_builder.py
import networkx as nx
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString
import logging
from typing import Dict, Any, Optional
from .osm_importer import OSMImporter
from .geospatial.geo_utils import haversine_distance

logger = logging.getLogger(__name__)

class NetworkBuilder:
    """Build and augment the road network with attributes for simulation and routing."""

    def __init__(self, importer: OSMImporter):
        self.importer = importer
        self.graph = importer.get_graph()
        self.gdf_nodes = importer.get_nodes_gdf()
        self.gdf_edges = importer.get_edges_gdf()

    def add_edge_speed(self, default_speed_kmh: float = 50.0):
        """Add speed attribute to edges if missing."""
        for u, v, key, data in self.graph.edges(data=True, keys=True):
            if 'speed_kph' not in data or pd.isna(data['speed_kph']):
                data['speed_kph'] = default_speed_kmh
        return self.graph

    def add_edge_travel_time(self):
        """Compute travel time in seconds from length and speed."""
        for u, v, key, data in self.graph.edges(data=True, keys=True):
            length_m = data.get('length', 0)
            speed_kph = data.get('speed_kph', 50)
            if speed_kph > 0:
                travel_time = length_m / (speed_kph * 1000 / 3600)  # seconds
            else:
                travel_time = 0
            data['travel_time'] = travel_time
        return self.graph

    def add_edge_lanes(self, default_lanes: int = 2):
        for u, v, key, data in self.graph.edges(data=True, keys=True):
            if 'lanes' not in data or pd.isna(data['lanes']):
                data['lanes'] = default_lanes
        return self.graph

    def build_network(self) -> nx.MultiDiGraph:
        """Apply all augmentations."""
        self.add_edge_speed()
        self.add_edge_travel_time()
        self.add_edge_lanes()
        return self.graph

    def get_nearest_node(self, lat: float, lon: float, method: str = 'haversine') -> int:
        """Find nearest OSM node ID to given coordinates."""
        # OSMnx has a function but we can implement manually for speed
        from .geospatial.geo_utils import haversine_distance
        node_gdf = self.gdf_nodes
        # Compute distance to each node (inefficient for large, but okay for demo)
        # In production use a spatial index like R-tree
        distances = node_gdf.geometry.apply(lambda pt: haversine_distance(lat, lon, pt.y, pt.x))
        nearest_idx = distances.idxmin()
        return node_gdf.loc[nearest_idx].name  # OSM node ID

    def get_edges_intersecting_bbox(self, min_lat: float, max_lat: float, min_lon: float, max_lon: float) -> gpd.GeoDataFrame:
        """Return edges that intersect the given bounding box."""
        bbox_polygon = gpd.GeoSeries([Polygon([
            (min_lon, min_lat), (max_lon, min_lat), (max_lon, max_lat), (min_lon, max_lat)
        ])])
        edges = self.gdf_edges
        # Use spatial index if available
        return edges[edges.intersects(bbox_polygon.unary_union)]