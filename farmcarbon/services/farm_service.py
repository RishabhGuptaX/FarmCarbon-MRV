"""Farm registration and lifecycle operations."""
from __future__ import annotations
from farmcarbon.storage.repository import Repository
from farmcarbon.services.geometry_service import parse_geojson, geodesic_area_ha, centroid_lon_lat
from farmcarbon.utils.validators import validate_coordinate

class FarmService:
    def __init__(self, repo: Repository, uploads_dir=None):
        self.repo, self.uploads_dir = repo, uploads_dir

    def register(self, payload: dict, boundary_geojson=None):
        boundary = parse_geojson(boundary_geojson) if boundary_geojson else None
        if boundary:
            payload["area_ha"] = round(geodesic_area_ha(boundary), 4)
            lon, lat = centroid_lon_lat(boundary)
            payload["longitude"], payload["latitude"] = lon, lat
        else:
            payload["area_ha"] = float(payload.get("area_ha") or 0)
            payload["latitude"], payload["longitude"] = validate_coordinate(payload.get("latitude"), payload.get("longitude"))
            if payload["area_ha"] <= 0:
                raise ValueError("Farm area must be greater than zero when no boundary is uploaded")
        if not payload.get("name", "").strip():
            raise ValueError("Farm name is required")
        payload["boundary_geojson"] = boundary
        farm = self.repo.create("farms", payload)
        self.repo.audit(farm["id"], "farm", farm["id"], "CREATE", "Farm registered")
        return farm

    def update(self, farm_id: str, changes: dict):
        farm = self.repo.update("farms", farm_id, changes)
        if farm:
            self.repo.audit(farm_id, "farm", farm_id, "UPDATE", "Farm details updated")
        return farm

    def replace_boundary(self, farm_id: str, boundary_geojson):
        boundary = parse_geojson(boundary_geojson)
        area = round(geodesic_area_ha(boundary), 4)
        lon, lat = centroid_lon_lat(boundary)
        updated = self.repo.update("farms", farm_id, {
            "boundary_geojson": boundary, "area_ha": area,
            "longitude": lon, "latitude": lat,
        })
        if updated:
            self.repo.audit(farm_id, "farm_boundary", farm_id, "REPLACE", "Farm boundary replaced and geodesic area recalculated")
        return updated

    def delete(self, farm_id: str):
        self.repo.delete_farm_cascade(farm_id, self.uploads_dir)
