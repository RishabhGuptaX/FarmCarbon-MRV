import json
from farmcarbon.storage.json_store import JsonStore
from farmcarbon.storage.repository import Repository


def test_json_store_crud(tmp_path):
    store=JsonStore(tmp_path); repo=Repository(store)
    record=repo.create("farms",{"name":"Test farm"})
    assert repo.get("farms",record["id"])["name"]=="Test farm"
    repo.update("farms",record["id"],{"name":"Updated"})
    assert repo.get("farms",record["id"])["name"]=="Updated"
    assert repo.delete("farms",record["id"])
    assert repo.get("farms",record["id"]) is None
    parsed=json.loads((tmp_path/"farms.json").read_text())
    assert parsed==[]
