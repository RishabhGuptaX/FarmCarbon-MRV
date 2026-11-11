"""Build shared application services."""
from config.settings import settings
from farmcarbon.storage.initializer import initialize_storage
from farmcarbon.storage.repository import Repository
from farmcarbon.demo_data import seed_demo_data
from farmcarbon.providers.satellite.demo_provider import DemoSatelliteProvider
from farmcarbon.providers.satellite.earth_engine_provider import EarthEngineProvider
from farmcarbon.services.farm_service import FarmService
from farmcarbon.services.practice_service import PracticeService
from farmcarbon.services.satellite_service import SatelliteService
from farmcarbon.services.mrv_service import MRVService


def build_runtime(seed_demo: bool = True):
    store = initialize_storage()
    repo = Repository(store)
    if seed_demo:
        seed_demo_data(repo)
    provider = DemoSatelliteProvider()
    provider_notice = "Demo provider active: observations are synthetic."
    if settings.satellite_provider in ("earth_engine", "gee"):
        try:
            provider = EarthEngineProvider(settings.ee_project_id)
            provider_notice = "Google Earth Engine is active."
        except Exception as exc:
            provider_notice = f"Earth Engine unavailable; using synthetic demo provider. Reason: {exc}"
    return {
        "store": store, "repo": repo, "farm_service": FarmService(repo, settings.uploads_dir),
        "practice_service": PracticeService(repo, settings.uploads_dir),
        "satellite_service": SatelliteService(repo, provider), "satellite_provider": provider,
        "provider_notice": provider_notice, "mrv_service": MRVService(repo),
    }
