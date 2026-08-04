# digital_twin/geospatial/geo_utils.py
import math
from typing import Tuple, Optional
import shapely.geometry as geom

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance in meters."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def point_to_linestring_distance(point: Tuple[float, float], linestring: geom.LineString) -> float:
    """Distance from point (lon, lat) to a LineString in meters."""
    pt = geom.Point(point)
    return pt.distance(linestring) * 111320  # approximate conversion degree to meters at equator

def project_point_to_line(point: Tuple[float, float], line: geom.LineString) -> Tuple[float, float]:
    """Find closest point on line to the given point, return (lon, lat)."""
    pt = geom.Point(point)
    nearest = pt.project(line, normalized=True)
    closest = line.interpolate(nearest, normalized=True)
    return (closest.x, closest.y)