"""Soil organic carbon stock calculations and comparable-zone analysis."""
from __future__ import annotations
from typing import Any


def calculate_soc_stock(soc_g_kg: float, bulk_density_g_cm3: float,
                        coarse_fragment_fraction: float, depth_cm: float) -> float:
    """Calculate fixed-depth SOC stock in Mg C/ha.

    Formula: SOC(g/kg) * bulk density(g/cm3) * (1 - coarse fragments) * depth(cm) * 0.1.
    This is a fixed-depth estimate; it is not equivalent-soil-mass adjusted.
    """
    values = (soc_g_kg, bulk_density_g_cm3, coarse_fragment_fraction, depth_cm)
    if any(v is None for v in values):
        raise ValueError("All soil-carbon inputs are required")
    if soc_g_kg < 0:
        raise ValueError("SOC concentration cannot be negative")
    if not 0 < bulk_density_g_cm3 <= 3:
        raise ValueError("Bulk density must be greater than 0 and no more than 3 g/cm³")
    if not 0 <= coarse_fragment_fraction < 1:
        raise ValueError("Coarse fragment fraction must be in the range [0, 1)")
    if depth_cm <= 0:
        raise ValueError("Sampling depth must be positive")
    return float(soc_g_kg * bulk_density_g_cm3 * (1 - coarse_fragment_fraction) * depth_cm * 0.1)


def compare_samples(samples: list[dict[str, Any]], farm_area_ha: float | None = None) -> dict[str, Any]:
    """Pair one baseline/follow-up sample per farm-zone-depth-method group.

    Pairs require the same farm, zone, depth interval and documented measurement
    method/provenance. The latest baseline is paired with the latest subsequent
    follow-up, avoiding accidental double counting when a zone has repeat samples.
    """
    baselines = [s for s in samples if s.get("measurement_period") == "Baseline"]
    followups = [s for s in samples if s.get("measurement_period") in ("Monitoring", "Follow-up", "Follow up")]
    groups: dict[tuple, list[dict[str, Any]]] = {}
    for base in baselines:
        method = (base.get("measurement_method") or "").strip().casefold()
        if not method or not base.get("source_mode"):
            continue
        key = (base.get("farm_id"), base.get("zone_id"),
               float(base.get("depth_top_cm", -1)), float(base.get("depth_bottom_cm", -1)), method)
        groups.setdefault(key, []).append(base)

    results: list[dict[str, Any]] = []
    warnings: list[str] = []
    for key, candidates_base in groups.items():
        baseline = sorted(candidates_base, key=lambda s: s.get("sample_date", ""))[-1]
        farm_id, zone_id, top, bottom, method = key
        compatible = [f for f in followups if
            f.get("farm_id") == farm_id and f.get("zone_id") == zone_id and
            float(f.get("depth_top_cm", -1)) == top and
            float(f.get("depth_bottom_cm", -1)) == bottom and
            (f.get("measurement_method") or "").strip().casefold() == method and
            bool(f.get("source_mode")) and
            (f.get("sample_date") or "") >= (baseline.get("sample_date") or "")]
        if not compatible:
            warnings.append(f"No compatible subsequent follow-up sample for zone {zone_id or 'unknown'} (matching farm, zone, depth, method and provenance required).")
            continue
        follow = sorted(compatible, key=lambda s: s.get("sample_date", ""))[-1]
        baseline_stock = float(baseline.get("calculated_soc_stock_mg_c_ha", 0))
        followup_stock = float(follow.get("calculated_soc_stock_mg_c_ha", 0))
        delta = followup_stock - baseline_stock
        zone_area = follow.get("zone_area_ha") or baseline.get("zone_area_ha") or farm_area_ha
        carbon_change = delta * float(zone_area) if zone_area else None
        results.append({
            "zone_id": zone_id, "baseline_sample_id": baseline.get("id"),
            "followup_sample_id": follow.get("id"), "baseline_stock_mg_c_ha": baseline_stock,
            "followup_stock_mg_c_ha": followup_stock, "stock_change_mg_c_ha": delta,
            "zone_area_ha": float(zone_area) if zone_area else None,
            "carbon_stock_change_mg_c": carbon_change,
            "co2e_change_mg": carbon_change * 44 / 12 if carbon_change is not None else None,
            "bulk_density_changed": abs(float(baseline.get("bulk_density_g_cm3", 0)) - float(follow.get("bulk_density_g_cm3", 0))) > 1e-9,
            "baseline_date": baseline.get("sample_date"), "followup_date": follow.get("sample_date"),
        })
    if any(r["bulk_density_changed"] for r in results):
        warnings.append("Bulk density differs between one or more paired periods. Equivalent soil mass adjustment may be necessary; this MVP reports fixed-depth results only.")
    if not results:
        warnings.append("No valid comparable baseline/follow-up measurements are available; no farm-wide stock change is calculated.")
    return {"comparisons": results, "warnings": warnings,
            "total_carbon_stock_change_mg_c": sum(r["carbon_stock_change_mg_c"] for r in results if r["carbon_stock_change_mg_c"] is not None) if results else None,
            "total_co2e_change_mg": sum(r["co2e_change_mg"] for r in results if r["co2e_change_mg"] is not None) if results else None}
