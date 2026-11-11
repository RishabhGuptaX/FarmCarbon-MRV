"""Application paths and configuration. No database is used by FarmCarbon MRV."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

@dataclass(frozen=True)
class Settings:
    root: Path = ROOT_DIR
    storage_dir: Path = ROOT_DIR / "storage"
    data_dir: Path = ROOT_DIR / "storage" / "data"
    uploads_dir: Path = ROOT_DIR / "storage" / "uploads"
    exports_dir: Path = ROOT_DIR / "data" / "exports"
    demo_dir: Path = ROOT_DIR / "data" / "demo"
    satellite_provider: str = os.getenv("FARMCARBON_SATELLITE_PROVIDER", "demo").lower()
    ee_project_id: str = os.getenv("EE_PROJECT_ID", "")

settings = Settings()
