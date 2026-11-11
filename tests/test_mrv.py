from farmcarbon.storage.json_store import JsonStore
from farmcarbon.storage.repository import Repository
from farmcarbon.services.mrv_service import MRVService


def test_mrv_status_and_explicit_review(tmp_path):
    repo=Repository(JsonStore(tmp_path))
    farm=repo.create("farms",{"name":"Test","baseline_date":"2025-01-01","boundary_geojson":{"type":"Polygon","coordinates":[]}})
    service=MRVService(repo)
    assessment=service.assess(farm)
    assert assessment["completeness_score"]<100
    review=service.record_review(farm["id"],"Named Reviewer","Reviewed limitations")
    assert review["status"]=="Review Completed"
    assert review["reviewer_name"]=="Named Reviewer"
