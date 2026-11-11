"""Lightweight type definitions for the JSON records."""
from __future__ import annotations
from typing import TypedDict, Any

class FarmRecord(TypedDict, total=False):
    id: str
    name: str
    project_identifier: str
    country: str
    state: str
    district: str
    village: str
    latitude: float
    longitude: float
    area_ha: float
    boundary_geojson: dict[str, Any] | None
    crop: str
    soil_type: str
    farming_system: str
    project_start_date: str
    baseline_date: str
    description: str
    created_at: str
    updated_at: str

class SoilSampleRecord(TypedDict, total=False):
    id: str
    farm_id: str
    zone_id: str
    sample_identifier: str
    sample_date: str
    depth_top_cm: float
    depth_bottom_cm: float
    soc_g_kg: float
    bulk_density_g_cm3: float
    coarse_fragment_fraction: float
    calculated_soc_stock_mg_c_ha: float
    measurement_period: str
    measurement_method: str
    source_mode: str
