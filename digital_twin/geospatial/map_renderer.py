# digital_twin/geospatial/map_renderer.py
import folium
from shapely.geometry import Point, LineString
import geopandas as gpd
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class MapRenderer:
    """Generate static map images using Folium (for debugging/thumbnails)."""

    @staticmethod
    def render_network(
        nodes_gdf: gpd.GeoDataFrame,
        edges_gdf: gpd.GeoDataFrame,
        center: tuple = (28.6139, 77.2090),
        zoom_start: int = 12,
        output_file: str = "twin_network.html",
    ):
        """Render the road network as an interactive Folium map."""
        m = folium.Map(location=center, zoom_start=zoom_start)

        # Add edges as polyline layers
        for _, row in edges_gdf.iterrows():
            geom = row.geometry
            if geom.geom_type == "LineString":
                coords = list(geom.coords)
                # folium expects [lat, lng]
                latlng = [(c[1], c[0]) for c in coords]
                folium.PolyLine(
                    locations=latlng,
                    color="blue",
                    weight=2,
                    opacity=0.6,
                ).add_to(m)

        # Add nodes as markers
        for _, row in nodes_gdf.iterrows():
            point = row.geometry
            folium.CircleMarker(
                location=(point.y, point.x),
                radius=3,
                color="red",
                fill=True,
                fillColor="red",
                fillOpacity=0.8,
                popup=f"Junction {row['junction_id']}",
            ).add_to(m)

        m.save(output_file)
        logger.info(f"Map saved to {output_file}")
        return m

    @staticmethod
    def render_ripple_heatmap(
        junctions: List[dict],
        affected_junctions: List[str],
        output_file: str = "ripple_heatmap.html",
    ):
        """Render a heatmap of ripple effects."""
        m = folium.Map(location=(28.6139, 77.2090), zoom_start=12)
        # Create heatmap data from affected junctions
        data = []
        for j in junctions:
            if j["id"] in affected_junctions:
                # Weight based on propagation strength
                weight = 1.0
                data.append([j["lat"], j["lng"], weight])
        if data:
            from folium.plugins import HeatMap
            HeatMap(data).add_to(m)
        m.save(output_file)
        return m