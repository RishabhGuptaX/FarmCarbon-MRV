"""GeoJSON validation and geodesic area calculations."""
from __future__ import annotations
import json
from typing import Any
from pyproj import Geod
from shapely.geometry import shape, mapping
from shapely.validation import explain_validity

_GEOD = Geod(ellps="WGS84")


def parse_geojson(payload: str | bytes | dict[str, Any]) -> dict[str, Any]:
    try:
        obj = json.loads(payload) if isinstance(payload, (str, bytes)) else payload
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Invalid GeoJSON: {exc}") from exc
    if not isinstance(obj, dict):
        raise ValueError("GeoJSON must be an object")
    if obj.get("type") == "FeatureCollection":
        features = obj.get("features") or []
        if len(features) != 1:
            raise ValueError("Upload a GeoJSON containing exactly one Polygon or MultiPolygon feature")
        geometry = features[0].get("geometry")
    elif obj.get("type") == "Feature":
        geometry = obj.get("geometry")
    else:
        geometry = obj
    if not isinstance(geometry, dict) or geometry.get("type") not in ("Polygon", "MultiPolygon"):
        raise ValueError("Farm boundary must be a Polygon or MultiPolygon")
    geom = shape(geometry)
    if geom.is_empty or not geom.is_valid:
        raise ValueError(f"Invalid farm boundary: {explain_validity(geom)}")
    if geom.area <= 0:
        raise ValueError("Farm boundary has zero area")
    # Return a canonical geometry object, not a Feature wrapper.
    return mapping(geom)


def geodesic_area_ha(geometry: dict[str, Any]) -> float:
    geom = shape(geometry)
    if geom.geom_type not in ("Polygon", "MultiPolygon") or not geom.is_valid:
        raise ValueError("A valid Polygon or MultiPolygon is required")
    area_m2, _ = _GEOD.geometry_area_perimeter(geom)
    return abs(float(area_m2)) / 10_000.0


def centroid_lon_lat(geometry: dict[str, Any]) -> tuple[float, float]:
    centroid = shape(geometry).centroid
    return float(centroid.x), float(centroid.y)


def feature_collection(geometry: dict[str, Any], properties: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": properties or {}, "geometry": geometry}]}
