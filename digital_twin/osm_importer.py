# digital_twin/osm_importer.py
import os
import json
import logging
from typing import Tuple, Optional
import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import Polygon
from .config import load_config

logger = logging.getLogger(__name__)

class OSMImporter:
    """Fetch and cache OpenStreetMap data for a city or bounding box."""

    def __init__(self, config_path: str = "digital_twin/config.yaml"):
        self.config = load_config(config_path)
        self.bounding_box = self.config.get("bounding_box")
        self.city = self.config.get("city")
        self.network_type = self.config.get("network_type", "drive")
        self.data_dir = self.config.get("data_dir", "./data/osm")
        os.makedirs(self.data_dir, exist_ok=True)
        self._graph = None
        self._gdf_nodes = None
        self._gdf_edges = None

    def _get_cache_path(self) -> str:
        """Generate a cache filename based on city/bounding box."""
        if self.city:
            return os.path.join(self.data_dir, f"{self.city.replace(' ', '_')}_{self.network_type}.graphml")
        else:
            bbox = self.bounding_box
            return os.path.join(self.data_dir, f"bbox_{bbox['min_lat']}_{bbox['max_lat']}_{bbox['min_lon']}_{bbox['max_lon']}_{self.network_type}.graphml")

    def load_or_fetch(self) -> nx.MultiDiGraph:
        """Load graph from cache or fetch from OSM."""
        cache_path = self._get_cache_path()
        if os.path.exists(cache_path) and self.config.get("osm_cache", True):
            logger.info(f"Loading OSM graph from cache: {cache_path}")
            self._graph = ox.load_graphml(cache_path)
            return self._graph

        logger.info(f"Fetching OSM data for {self.city or self.bounding_box}")
        if self.city:
            graph = ox.graph_from_place(
                self.city,
                network_type=self.network_type,
                simplify=True,
            )
        elif self.bounding_box:
            bbox = self.bounding_box
            polygon = Polygon([
                (bbox['min_lon'], bbox['min_lat']),
                (bbox['max_lon'], bbox['min_lat']),
                (bbox['max_lon'], bbox['max_lat']),
                (bbox['min_lon'], bbox['max_lat']),
            ])
            graph = ox.graph_from_polygon(
                polygon,
                network_type=self.network_type,
                simplify=True,
            )
        else:
            raise ValueError("Either city or bounding_box must be provided.")

        # Simplify and clean
        graph = ox.project_graph(graph, to_latlong=True)
        # Cache
        ox.save_graphml(graph, cache_path)
        self._graph = graph
        return graph

    def get_graph(self) -> nx.MultiDiGraph:
        if self._graph is None:
            self._graph = self.load_or_fetch()
        return self._graph

    def get_nodes_gdf(self) -> gpd.GeoDataFrame:
        if self._gdf_nodes is None:
            graph = self.get_graph()
            self._gdf_nodes, self._gdf_edges = ox.graph_to_gdfs(graph)
        return self._gdf_nodes

    def get_edges_gdf(self) -> gpd.GeoDataFrame:
        if self._gdf_edges is None:
            self.get_nodes_gdf()  # fills both
        return self._gdf_edges

    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """Return (min_lat, max_lat, min_lon, max_lon)."""
        gdf = self.get_nodes_gdf()
        total_bounds = gdf.total_bounds  # [minx, miny, maxx, maxy] = [lon_min, lat_min, lon_max, lat_max]
        return total_bounds[1], total_bounds[3], total_bounds[0], total_bounds[2]