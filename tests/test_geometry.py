import pytest
from farmcarbon.services.geometry_service import parse_geojson, geodesic_area_ha, centroid_lon_lat


def polygon():
    return {"type":"Polygon","coordinates":[[[80,16],[80.01,16],[80.01,16.01],[80,16.01],[80,16]]]}


def test_geojson_area_and_centroid():
    geom=parse_geojson(polygon())
    assert geodesic_area_ha(geom)>0
    lon,lat=centroid_lon_lat(geom)
    assert 80<lon<80.01 and 16<lat<16.01


def test_rejects_invalid_type():
    with pytest.raises(ValueError): parse_geojson({"type":"Point","coordinates":[0,0]})


def test_rejects_self_intersection():
    bad={"type":"Polygon","coordinates":[[[0,0],[1,1],[0,1],[1,0],[0,0]]]}
    with pytest.raises(ValueError): parse_geojson(bad)
