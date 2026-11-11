"""Input validation helpers."""
from __future__ import annotations
from datetime import date


def validate_coordinate(latitude, longitude):
    if latitude is None or longitude is None:
        raise ValueError("Latitude and longitude are required")
    if not -90 <= float(latitude) <= 90:
        raise ValueError("Latitude must be between -90 and 90")
    if not -180 <= float(longitude) <= 180:
        raise ValueError("Longitude must be between -180 and 180")
    return float(latitude), float(longitude)


def validate_date_range(start: date, end: date):
    if end < start:
        raise ValueError("End date must be on or after start date")
