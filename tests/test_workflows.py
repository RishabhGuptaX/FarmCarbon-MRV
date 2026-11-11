from datetime import date, timedelta
from farmcarbon.storage.json_store import JsonStore
from farmcarbon.storage.repository import Repository
from farmcarbon.services.farm_service import FarmService
from farmcarbon.providers.satellite.demo_provider import DemoSatelliteProvider


def test_farm_boundary_register_and_replace(tmp_path):
    repo=Repository(JsonStore(tmp_path/"data"))
    service=FarmService(repo,tmp_path/"uploads")
    first={"type":"Polygon","coordinates":[[[80,16],[80.01,16],[80.01,16.01],[80,16.01],[80,16]]]}
    farm=service.register({"name":"Boundary test"},first)
    assert farm["area_ha"]>0
    old_area=farm["area_ha"]
    second={"type":"Polygon","coordinates":[[[80,16],[80.02,16],[80.02,16.02],[80,16.02],[80,16]]]}
    updated=service.replace_boundary(farm["id"],second)
    assert updated["area_ha"]>old_area
    assert updated["boundary_geojson"]["type"]=="Polygon"


def test_demo_provider_returns_synthetic_labelled_series():
    farm={"id":"farm-demo"}
    observations=DemoSatelliteProvider().get_observations(farm,date(2025,1,1),date(2025,12,31),100)
    assert len(observations)>=12
    assert all(row["source_mode"]=="DEMO" for row in observations)
    assert all(row["source_collection"]=="DEMO_SYNTHETIC_SENTINEL2_LIKE" for row in observations)
