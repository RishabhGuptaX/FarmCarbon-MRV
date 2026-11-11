"""Deterministic synthetic observation provider for offline demonstrations."""
from __future__ import annotations
from datetime import timedelta
import math
import hashlib
from farmcarbon.providers.satellite.base import SatelliteProvider

class DemoSatelliteProvider(SatelliteProvider):
    mode = "demo"
    def get_observations(self, farm, start_date, end_date, cloud_threshold=30):
        if end_date < start_date:
            raise ValueError("End date must be on or after start date")
        seed = int(hashlib.sha256(str(farm.get("id", "demo")).encode()).hexdigest()[:8], 16)
        observations, current, index = [], start_date, 0
        while current <= end_date:
            # One observation roughly every 30 days, with reproducible synthetic seasonal variation.
            seasonal = 0.08 * math.sin((current.timetuple().tm_yday / 365) * 2 * math.pi)
            ndvi = min(0.9, max(0.05, 0.52 + seasonal + ((seed % 13) - 6) / 100 + 0.012 * math.sin(index)))
            ndmi = min(0.7, max(-0.2, 0.18 + 0.55 * (ndvi - 0.4) + 0.03 * math.cos(index * 0.8)))
            evi = min(1.0, max(-0.2, 2.5 * (ndvi - 0.12) / (1 + 5.5 * ndvi)))
            cloud = float((seed + index * 17) % 46)
            if cloud <= cloud_threshold:
                observations.append({
                    "observation_date": current.isoformat(), "ndvi": round(ndvi, 4),
                    "ndmi": round(ndmi, 4), "evi": round(evi, 4),
                    "cloud_percentage": round(cloud, 1), "source": "Synthetic demonstration provider",
                    "source_collection": "DEMO_SYNTHETIC_SENTINEL2_LIKE",
                    "source_mode": "DEMO", "algorithm_version": "demo-indices-v1",
                    "metadata_json": {"synthetic": True, "seed": seed, "note": "Not observed satellite data"},
                })
            current += timedelta(days=30)
            index += 1
        return observations
