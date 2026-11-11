"""Reusable calculations exported for tests and simple scripts."""
from farmcarbon.services.soil_carbon_service import calculate_soc_stock
from farmcarbon.services.geometry_service import geodesic_area_ha

__all__ = ["calculate_soc_stock", "geodesic_area_ha"]
