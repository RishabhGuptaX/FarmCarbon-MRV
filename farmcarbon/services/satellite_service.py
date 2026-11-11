"""Satellite observation workflows, independent of any UI framework."""
from __future__ import annotations
from datetime import date
from farmcarbon.storage.repository import Repository

class SatelliteService:
    def __init__(self, repo: Repository, provider):
        self.repo, self.provider = repo, provider

    def collect(self, farm: dict, start_date: date, end_date: date, cloud_threshold: float = 30):
        observations = self.provider.get_observations(farm, start_date, end_date, cloud_threshold)
        saved = []
        for obs in observations:
            # Avoid duplicate imports of the same farm/date/source/mode.
            existing = self.repo.list("satellite_observations", farm_id=farm["id"])
            if any(x.get("observation_date") == obs.get("observation_date") and x.get("source") == obs.get("source") and x.get("source_mode") == obs.get("source_mode") for x in existing):
                continue
            saved.append(self.repo.create("satellite_observations", {"farm_id": farm["id"], **obs}))
        self.repo.audit(farm["id"], "satellite_observation", farm["id"], "IMPORT", f"Saved {len(saved)} satellite observations", self.provider.mode.upper())
        return saved
