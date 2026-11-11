"""Optional Google Earth Engine Sentinel-2 provider.

Install earthengine-api separately, set EE_PROJECT_ID, then run
`earthengine authenticate`. The application remains usable without this provider.
"""
from __future__ import annotations
from datetime import date
import json
from farmcarbon.providers.satellite.base import SatelliteProvider

class EarthEngineProvider(SatelliteProvider):
    mode = "earth_engine"
    COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"

    def __init__(self, project_id: str):
        if not project_id:
            raise ValueError("EE_PROJECT_ID is required for Earth Engine")
        try:
            import ee
        except ImportError as exc:
            raise RuntimeError("Optional package earthengine-api is not installed") from exc
        try:
            ee.Initialize(project=project_id)
        except Exception as exc:
            raise RuntimeError(f"Earth Engine initialisation failed. Authenticate locally with `earthengine authenticate`. Details: {exc}") from exc
        self.ee = ee

    def get_observations(self, farm, start_date: date, end_date: date, cloud_threshold=30):
        ee = self.ee
        boundary = farm.get("boundary_geojson")
        if not boundary:
            raise ValueError("A farm GeoJSON boundary is required for Earth Engine")
        geom = ee.Geometry(boundary)
        # Mask SCL cloud shadow, clouds, cirrus and snow/ice classes (3, 8, 9, 10, 11).
        def mask_and_indices(image):
            scl = image.select("SCL")
            clear = scl.neq(3).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10)).And(scl.neq(11))
            image = image.updateMask(clear)
            # Sentinel-2 SR optical bands are stored as scaled integers (scale factor 1e-4).
            # Convert to reflectance before EVI because its denominator includes an additive 1.
            red, nir, green, swir, blue = [image.select(b).multiply(0.0001) for b in ("B4", "B8", "B3", "B11", "B2")]
            ndvi = nir.subtract(red).divide(nir.add(red)).rename("NDVI")
            ndmi = nir.subtract(swir).divide(nir.add(swir)).rename("NDMI")
            evi = nir.subtract(red).multiply(2.5).divide(nir.add(red.multiply(6)).subtract(blue.multiply(7.5)).add(1)).rename("EVI")
            return image.addBands([ndvi, ndmi, evi])
        collection = (ee.ImageCollection(self.COLLECTION)
            .filterBounds(geom)
            .filterDate(start_date.isoformat(), (end_date + __import__('datetime').timedelta(days=1)).isoformat())
            .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", float(cloud_threshold)))
            .map(mask_and_indices))
        count = collection.size().getInfo()
        if not count:
            return []
        images = collection.sort("system:time_start").toList(count)
        observations = []
        for idx in range(count):
            image = ee.Image(images.get(idx))
            stats = image.select(["NDVI", "NDMI", "EVI"]).reduceRegion(
                reducer=ee.Reducer.mean(), geometry=geom, scale=20, maxPixels=1e8, bestEffort=True
            ).getInfo() or {}
            info = image.toDictionary(["system:time_start", "CLOUDY_PIXEL_PERCENTAGE", "PRODUCT_ID"]).getInfo()
            if any(stats.get(k) is None for k in ("NDVI", "NDMI", "EVI")):
                continue
            from datetime import datetime, timezone
            obs_date = datetime.fromtimestamp(info["system:time_start"] / 1000, timezone.utc).date().isoformat()
            observations.append({
                "observation_date": obs_date, "ndvi": round(float(stats["NDVI"]), 5),
                "ndmi": round(float(stats["NDMI"]), 5), "evi": round(float(stats["EVI"]), 5),
                "cloud_percentage": float(info.get("CLOUDY_PIXEL_PERCENTAGE", 0)),
                "source": "Google Earth Engine", "source_collection": self.COLLECTION,
                "source_mode": "LIVE", "algorithm_version": "s2-scl-mask-v1",
                "metadata_json": {"product_id": info.get("PRODUCT_ID"), "mask": "SCL classes 3,8,9,10,11 excluded", "scale_m": 20},
            })
        return observations
