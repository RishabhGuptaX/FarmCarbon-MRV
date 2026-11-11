"""Seed and reset clearly labelled synthetic demonstration data."""
from __future__ import annotations
from datetime import date, timedelta
from farmcarbon.storage.repository import Repository
from farmcarbon.services.geometry_service import geodesic_area_ha, centroid_lon_lat
from farmcarbon.services.soil_carbon_service import calculate_soc_stock
from farmcarbon.providers.satellite.demo_provider import DemoSatelliteProvider
from farmcarbon.storage.json_store import COLLECTIONS


def _farm_geometry(lon, lat, delta=0.012):
    return {"type": "Polygon", "coordinates": [[[lon, lat], [lon + delta, lat], [lon + delta, lat + delta], [lon, lat + delta], [lon, lat]]]}


def seed_demo_data(repo: Repository, force: bool = False):
    if repo.list("farms") and not force:
        return False
    if force:
        repo.store.clear()
    today = date.today()
    definitions = [
        {"name": "Green Valley Demonstration Farm", "project_identifier": "FC-DEMO-001", "country": "India", "state": "Andhra Pradesh", "district": "Demo District A", "village": "Demo Village A", "crop": "Paddy", "soil_type": "Alluvial", "farming_system": "Rice-based", "description": "Synthetic demonstration farm for end-to-end FarmCarbon MRV workflows.", "lon": 80.12, "lat": 16.48},
        {"name": "Regenerative Fields Demo", "project_identifier": "FC-DEMO-002", "country": "India", "state": "Maharashtra", "district": "Demo District B", "village": "Demo Village B", "crop": "Cotton", "soil_type": "Black soil", "farming_system": "Mixed cropping", "description": "Synthetic second farm used to demonstrate multi-farm monitoring.", "lon": 75.72, "lat": 19.21},
    ]
    provider = DemoSatelliteProvider()
    for idx, spec in enumerate(definitions):
        geom = _farm_geometry(spec.pop("lon"), spec.pop("lat"))
        lon, lat = centroid_lon_lat(geom)
        farm = repo.create("farms", {
            **spec, "latitude": lat, "longitude": lon, "area_ha": round(geodesic_area_ha(geom), 4),
            "boundary_geojson": geom, "project_start_date": (today - timedelta(days=400)).isoformat(),
            "baseline_date": (today - timedelta(days=365)).isoformat(), "source_mode": "DEMO",
        })
        observations = provider.get_observations(farm, today - timedelta(days=365), today, 45)
        for observation in observations:
            repo.create("satellite_observations", {"farm_id": farm["id"], **observation})
        repo.create("practices", {
            "farm_id": farm["id"], "zone_id": "ZONE-01", "practice_type": "Cover Cropping" if idx == 0 else "Reduced Tillage",
            "start_date": (today - timedelta(days=180)).isoformat(), "end_date": None,
            "area_ha": round(farm["area_ha"] * 0.65, 3), "crop": farm["crop"], "quantity": None,
            "unit": None, "status": "Implemented", "description": "Synthetic demonstration intervention record.", "source_mode": "DEMO",
        })
        repo.create("evidence_files", {
            "farm_id": farm["id"], "practice_id": None,
            "file_name": "Synthetic demo evidence metadata (no real attachment)",
            "stored_path": None, "file_type": "demo_metadata", "source_mode": "DEMO",
        })
        repo.audit(farm["id"], "farm", farm["id"], "SEED", "Synthetic demonstration farm created", "DEMO")
        if idx == 0:
            for period, days, soc in (("Baseline", 350, 10.0), ("Monitoring", 15, 11.2)):
                stock = calculate_soc_stock(soc, 1.3, 0.10, 30)
                repo.create("soil_samples", {
                    "farm_id": farm["id"], "zone_id": "ZONE-01", "zone_area_ha": 4.0,
                    "sample_identifier": f"DEMO-{period.upper()}-001", "sample_date": (today - timedelta(days=days)).isoformat(),
                    "latitude": lat, "longitude": lon, "depth_top_cm": 0, "depth_bottom_cm": 30,
                    "soc_g_kg": soc, "bulk_density_g_cm3": 1.3, "coarse_fragment_fraction": 0.10,
                    "measurement_method": "Walkley-Black (demo)", "laboratory_reference": "SYNTHETIC-LAB-REF",
                    "laboratory_attachment": None, "calculated_soc_stock_mg_c_ha": stock,
                    "measurement_period": period, "source_mode": "DEMO", "notes": "Synthetic soil value for demonstration only.",
                })
    return True
