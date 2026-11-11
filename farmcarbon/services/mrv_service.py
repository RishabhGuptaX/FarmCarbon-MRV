"""MRV completeness, review gating and data-quality checks."""
from __future__ import annotations
from farmcarbon.services.soil_carbon_service import compare_samples
from farmcarbon.services.geometry_service import parse_geojson
from farmcarbon.utils.validators import validate_coordinate

class MRVService:
    def __init__(self, repo):
        self.repo = repo

    def assess(self, farm: dict) -> dict:
        farm_id = farm["id"]
        soils = self.repo.list("soil_samples", farm_id=farm_id)
        sats = self.repo.list("satellite_observations", farm_id=farm_id)
        practices = self.repo.list("practices", farm_id=farm_id)
        evidence = self.repo.list("evidence_files", farm_id=farm_id)
        boundary_ok = bool(farm.get("boundary_geojson"))
        uploaded_evidence = [e for e in evidence if e.get("stored_path")]
        evidence_practice_ids = {e.get("practice_id") for e in uploaded_evidence if e.get("practice_id")}
        practices_missing_evidence = [p for p in practices if p.get("id") not in evidence_practice_ids]
        checks = [
            ("Farm registered", True, "Farm record exists."),
            ("Valid farm boundary", boundary_ok, "Upload a valid Polygon or MultiPolygon boundary." if not boundary_ok else "Boundary is stored as GeoJSON."),
            ("Baseline date recorded", bool(farm.get("baseline_date")), "Add a baseline date." if not farm.get("baseline_date") else "Baseline date is recorded."),
            ("Baseline soil sample", any(s.get("measurement_period") == "Baseline" for s in soils), "Add at least one baseline soil sample."),
            ("Agricultural intervention", bool(practices), "Record at least one agricultural practice."),
            ("Monitoring observations", bool(sats), "Import satellite observations or upload a monitoring CSV."),
            ("Follow-up soil measurement", any(s.get("measurement_period") in ("Monitoring", "Follow-up", "Follow up") for s in soils), "Required to report a measured SOC stock change."),
            ("Supporting evidence", bool(uploaded_evidence) and not practices_missing_evidence, "Upload an actual supporting image, CSV or PDF for every intervention."),
            ("Data provenance", all(bool(s.get("source_mode") and s.get("measurement_method")) for s in soils) if soils else False, "Record source mode and measurement method for soil samples."),
        ]
        score = round(sum(1 for _, ok, _ in checks if ok) / len(checks) * 100)
        warnings = []
        if not boundary_ok:
            warnings.append("Farm boundary is missing; spatial coverage cannot be confirmed.")
        else:
            try:
                parse_geojson(farm.get("boundary_geojson"))
            except Exception as exc:
                warnings.append(f"Farm geometry is invalid: {exc}")
        try:
            validate_coordinate(farm.get("latitude"), farm.get("longitude"))
        except Exception:
            warnings.append("Farm latitude/longitude is missing or outside valid coordinate ranges.")
        if not soils: warnings.append("No soil measurements are recorded.")
        for s in soils:
            if s.get("soc_g_kg") is None or float(s.get("soc_g_kg", -1)) < 0: warnings.append(f"Sample {s.get('sample_identifier', s.get('id'))}: invalid or missing SOC concentration.")
            if not s.get("bulk_density_g_cm3") or float(s.get("bulk_density_g_cm3", 0)) <= 0:
                warnings.append(f"Sample {s.get('sample_identifier', s.get('id'))}: bulk density is missing or invalid.")
            if not s.get("measurement_method") or not s.get("source_mode"):
                warnings.append(f"Sample {s.get('sample_identifier', s.get('id'))}: measurement method or data provenance is missing.")
            if float(s.get("depth_bottom_cm", 0)) <= float(s.get("depth_top_cm", 0)):
                warnings.append(f"Sample {s.get('sample_identifier', s.get('id'))}: depth interval is invalid.")
        for obs in sats:
            if float(obs.get("cloud_percentage") or 0) > 50: warnings.append(f"Satellite observation {obs.get('observation_date')} has high cloud cover.")
            if any(obs.get(key) is None for key in ("ndvi", "ndmi", "evi")):
                warnings.append(f"Satellite observation {obs.get('observation_date')} has missing indicator values.")
            if obs.get("source_mode") in ("DEMO", "SYNTHETIC"): warnings.append("Synthetic demo satellite observations are present; they are not real satellite measurements.")
            if obs.get("source_mode") == "UPLOAD": warnings.append("User-uploaded satellite observations require independent source review.")
        comparison = compare_samples(soils, farm.get("area_ha"))
        warnings.extend(comparison["warnings"])
        if practices_missing_evidence:
            warnings.append(f"{len(practices_missing_evidence)} intervention record(s) do not have an attached evidence file.")
        latest_review = sorted(self.repo.list("mrv_reviews", farm_id=farm_id), key=lambda r: r.get("created_at", ""))[-1:] 
        status = "Not Started"
        if not farm.get("baseline_date") or not boundary_ok:
            status = "Baseline Required"
        elif not any(s.get("measurement_period") == "Baseline" for s in soils):
            status = "Baseline Required"
        elif latest_review and latest_review[0].get("status") == "Review Completed":
            status = "Review Completed"
        elif practices_missing_evidence:
            status = "Evidence Incomplete"
        elif score == 100:
            status = "Ready for Review"
        elif sats or practices:
            status = "Monitoring Active"
        elif any(s.get("measurement_period") == "Baseline" for s in soils):
            status = "Baseline Recorded"
        return {"checks": checks, "completeness_score": score, "status": status,
                "warnings": list(dict.fromkeys(warnings)), "comparison": comparison}

    def record_review(self, farm_id: str, reviewer_name: str, notes: str = ""):
        if not reviewer_name.strip():
            raise ValueError("Reviewer name is required")
        farm = self.repo.get("farms", farm_id)
        if not farm:
            raise ValueError("Farm not found")
        assessment = self.assess(farm)
        return self.repo.create("mrv_reviews", {
            "farm_id": farm_id, "reporting_period_start": farm.get("project_start_date"),
            "reporting_period_end": None, "status": "Review Completed",
            "completeness_score": assessment["completeness_score"],
            "reviewer_name": reviewer_name.strip(), "reviewer_notes": notes,
            "reviewed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        })
